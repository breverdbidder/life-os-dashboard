import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import { CheckCircle, XCircle, Clock, TrendingUp, Brain, Dumbbell, Users, Briefcase } from 'lucide-react'

export default function Dashboard() {
  const [tasks, setTasks] = useState([])
  const [metrics, setMetrics] = useState(null)
  const [streak, setStreak] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    try {
      // Fetch recent tasks
      const { data: tasksData } = await supabase
        .from('tasks')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(10)

      // Fetch latest metrics
      const { data: metricsData } = await supabase
        .from('daily_metrics')
        .select('*')
        .order('date', { ascending: false })
        .limit(1)

      // Fetch streak
      const { data: streakData } = await supabase
        .from('task_completion_streaks')
        .select('*')
        .eq('user_id', 1)
        .single()

      setTasks(tasksData || [])
      setMetrics(metricsData?.[0] || null)
      setStreak(streakData || null)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      'COMPLETED': 'bg-green-100 text-green-800',
      'IN_PROGRESS': 'bg-blue-100 text-blue-800',
      'INITIATED': 'bg-yellow-100 text-yellow-800',
      'SOLUTION_PROVIDED': 'bg-purple-100 text-purple-800',
      'ABANDONED': 'bg-red-100 text-red-800',
      'BLOCKED': 'bg-gray-100 text-gray-800',
      'DEFERRED': 'bg-orange-100 text-orange-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getDomainIcon = (domain) => {
    const icons = {
      'BUSINESS': <Briefcase className="w-4 h-4" />,
      'MICHAEL': <Dumbbell className="w-4 h-4" />,
      'FAMILY': <Users className="w-4 h-4" />,
      'PERSONAL': <Brain className="w-4 h-4" />,
    }
    return icons[domain] || <Clock className="w-4 h-4" />
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading Life OS...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Shapira Life OS</h1>
              <p className="text-sm text-gray-500">ADHD-Optimized Productivity System</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">
                🕐 FL: {new Date().toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit' })} EST
              </div>
              <div className="text-sm text-gray-500">
                🕐 IL: {new Date().toLocaleTimeString('en-US', { timeZone: 'Asia/Jerusalem', hour: '2-digit', minute: '2-digit' })} IST
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {/* Streak Card */}
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Current Streak</p>
                <p className="text-3xl font-bold text-green-600">{streak?.current_streak || 0}</p>
                <p className="text-xs text-gray-400">Longest: {streak?.longest_streak || 0}</p>
              </div>
              <TrendingUp className="w-10 h-10 text-green-500 opacity-50" />
            </div>
          </div>

          {/* Completed Today */}
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Completed Today</p>
                <p className="text-3xl font-bold text-blue-600">{metrics?.tasks_completed || 0}</p>
              </div>
              <CheckCircle className="w-10 h-10 text-blue-500 opacity-50" />
            </div>
          </div>

          {/* Abandoned Today */}
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Abandoned Today</p>
                <p className="text-3xl font-bold text-red-600">{metrics?.tasks_abandoned || 0}</p>
              </div>
              <XCircle className="w-10 h-10 text-red-500 opacity-50" />
            </div>
          </div>

          {/* Completion Rate */}
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Completion Rate</p>
                <p className="text-3xl font-bold text-purple-600">
                  {metrics?.completion_rate ? `${metrics.completion_rate}%` : '--'}
                </p>
              </div>
              <Brain className="w-10 h-10 text-purple-500 opacity-50" />
            </div>
          </div>
        </div>

        {/* Tasks Section */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-4 py-3 border-b">
            <h2 className="text-lg font-semibold text-gray-900">Recent Tasks</h2>
          </div>
          
          {tasks.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No tasks yet. Start a conversation with Claude to track tasks.</p>
            </div>
          ) : (
            <div className="divide-y">
              {tasks.map((task) => (
                <div key={task.id} className="px-4 py-3 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        {getDomainIcon(task.domain)}
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                          {task.status}
                        </span>
                        {task.priority && (
                          <span className="text-xs text-gray-500">{task.priority}</span>
                        )}
                      </div>
                      <p className="text-sm text-gray-900">{task.description}</p>
                      <div className="flex gap-4 mt-1 text-xs text-gray-500">
                        {task.task_complexity && <span>Complexity: {task.task_complexity}/10</span>}
                        {task.estimated_time_minutes && <span>Est: {task.estimated_time_minutes}min</span>}
                        {task.actual_time_minutes && <span>Actual: {task.actual_time_minutes}min</span>}
                      </div>
                    </div>
                    <div className="text-xs text-gray-400">
                      {new Date(task.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Domain Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          <DomainCard icon={<Briefcase />} title="Business" subtitle="Everest Capital" color="blue" />
          <DomainCard icon={<Dumbbell />} title="Michael D1" subtitle="Swimming" color="green" />
          <DomainCard icon={<Users />} title="Family" subtitle="Shapira" color="purple" />
          <DomainCard icon={<Brain />} title="Personal" subtitle="Health & Learning" color="orange" />
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-8 py-4 text-center text-sm text-gray-500">
        Shapira Life OS v1.0 • Powered by Claude AI + Supabase
      </footer>
    </div>
  )
}

function DomainCard({ icon, title, subtitle, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    green: 'bg-green-50 border-green-200 text-green-700',
    purple: 'bg-purple-50 border-purple-200 text-purple-700',
    orange: 'bg-orange-50 border-orange-200 text-orange-700',
  }

  return (
    <div className={`rounded-lg border-2 p-4 ${colorClasses[color]}`}>
      <div className="flex items-center gap-3">
        <div className="opacity-70">{icon}</div>
        <div>
          <h3 className="font-semibold">{title}</h3>
          <p className="text-sm opacity-70">{subtitle}</p>
        </div>
      </div>
    </div>
  )
}
