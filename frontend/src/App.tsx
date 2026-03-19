import { useState } from 'react'
import { generateBlog, publishLinkedIn, publishWhatsApp, type GenerateResponse } from './api'

const TONES = ['Professional', 'Technical', 'Casual'] as const
const LENGTHS = ['Short', 'Medium', 'Long'] as const
const LENGTH_MAP: Record<string, string> = {
  Short: 'short',
  Medium: 'medium',
  Long: 'long',
}
const SAMPLE_TOPIC = 'The rise of AI-powered phishing attacks in 2025'

function App() {
  const [topic, setTopic] = useState('')
  const [tone, setTone] = useState<(typeof TONES)[number]>('Professional')
  const [length, setLength] = useState<(typeof LENGTHS)[number]>('Medium')
  const [generating, setGenerating] = useState(false)
  const [result, setResult] = useState<GenerateResponse | null>(null)
  const [linkedinPost, setLinkedinPost] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [publishing, setPublishing] = useState<'linkedin' | 'whatsapp' | null>(null)
  const [summaryOpen, setSummaryOpen] = useState(false)
  const [activeNav, setActiveNav] = useState<'create' | 'dashboard'>('create')

  const handleGenerate = async () => {
    if (!topic.trim()) return
    setError(null)
    setGenerating(true)
    setResult(null)
    try {
      const data = await generateBlog(topic.trim(), tone.toLowerCase(), LENGTH_MAP[length] || 'medium')
      setResult(data)
      setLinkedinPost(data.linkedin_post)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Generation failed')
    } finally {
      setGenerating(false)
    }
  }

  const handleLinkedIn = async () => {
    if (!result) return
    setPublishing('linkedin')
    setError(null)
    try {
      await publishLinkedIn(
        result.topic,
        result.summary,
        result.full_content,
        linkedinPost,
        result.thumbnail_url ? result.thumbnail_url.replace('/api/outputs/', '') : null
      )
    } catch (e) {
      setError(e instanceof Error ? e.message : 'LinkedIn failed')
    } finally {
      setPublishing(null)
    }
  }

  const handleWhatsApp = async () => {
    if (!result) return
    setPublishing('whatsapp')
    setError(null)
    try {
      await publishWhatsApp(result.topic, result.summary, result.sources || [])
    } catch (e) {
      setError(e instanceof Error ? e.message : 'WhatsApp failed')
    } finally {
      setPublishing(null)
    }
  }

  const handleNewPost = () => {
    setResult(null)
    setTopic('')
    setLinkedinPost('')
    setError(null)
    setActiveNav('create')
  }

  const thumbnailUrl = result?.thumbnail_url || null
  const wordCount = result?.full_content ? result.full_content.split(/\s+/).length : 0

  return (
    <div className="min-h-screen bg-[#f9fafb] flex flex-col">
      {/* Top navigation — Groq-style */}
      <header className="h-14 flex items-center justify-between px-4 sm:px-6 lg:px-8 bg-white border-b border-[#e5e7eb] sticky top-0 z-30">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-[#1d4ed8] flex items-center justify-center text-white font-bold text-sm">
              W
            </div>
            <span className="font-semibold text-[#111827] text-[15px] hidden sm:inline">wersec</span>
          </div>
          <div className="hidden md:flex items-center gap-1">
            <select className="text-sm font-medium text-[#374151] bg-transparent border-none cursor-pointer focus:ring-0 focus:outline-none py-1.5 px-2 rounded hover:bg-[#f3f4f6]">
              <option>Personal</option>
            </select>
            <span className="text-[#9ca3af]">/</span>
            <select className="text-sm font-medium text-[#374151] bg-transparent border-none cursor-pointer focus:ring-0 focus:outline-none py-1.5 px-2 rounded hover:bg-[#f3f4f6]">
              <option>Blog Generator</option>
            </select>
          </div>
        </div>
        <nav className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => { setActiveNav('create'); if (result) handleNewPost(); }}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition ${activeNav === 'create' ? 'text-[#1d4ed8] bg-[#eff6ff]' : 'text-[#6b7280] hover:text-[#111827] hover:bg-[#f3f4f6]'}`}
          >
            Create
          </button>
          <button
            type="button"
            onClick={() => setActiveNav('dashboard')}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition ${activeNav === 'dashboard' ? 'text-[#1d4ed8] bg-[#eff6ff]' : 'text-[#6b7280] hover:text-[#111827] hover:bg-[#f3f4f6]'}`}
          >
            Dashboard
          </button>
          <button type="button" className="p-2 rounded-lg text-[#6b7280] hover:bg-[#f3f4f6] hover:text-[#374151] transition">
            <SettingsIcon className="w-4 h-4" />
          </button>
          <div className="w-8 h-8 rounded-full bg-[#e5e7eb] flex items-center justify-center text-[#6b7280] text-xs font-medium ml-1">
            U
          </div>
        </nav>
      </header>

      <main className="flex-1 w-full max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {error && (
          <div className="mb-6 rounded-xl bg-[#fef2f2] border border-[#fecaca] px-4 py-3 text-sm text-[#b91c1c] flex items-center justify-between gap-4">
            <span>{error}</span>
            <button type="button" onClick={() => setError(null)} className="text-[#dc2626] hover:text-[#991b1b] shrink-0 font-medium">
              Dismiss
            </button>
          </div>
        )}

        {/* Hero card — value prop + metric + CTA */}
        <section className="bg-white rounded-2xl border border-[#e5e7eb] shadow-sm overflow-hidden mb-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 divide-y lg:divide-y-0 lg:divide-x divide-[#e5e7eb]">
            <div className="p-6 sm:p-8">
              <div className="w-10 h-10 rounded-xl bg-[#eff6ff] flex items-center justify-center text-[#1d4ed8] mb-4">
                <BoltIcon className="w-5 h-5" />
              </div>
              <h1 className="text-[1.25rem] font-semibold text-[#111827] tracking-tight mb-2">
                Create content fast with Wersec
              </h1>
              <p className="text-sm text-[#6b7280] leading-relaxed max-w-sm">
                Enter a cybersecurity topic. We research, write the article, and prepare a LinkedIn-ready post and cover image.
              </p>
            </div>
            <div className="p-6 sm:p-8 flex flex-col justify-center">
              <p className="text-label mb-1">Posts this session</p>
              <p className="text-2xl font-bold text-[#111827] tabular-nums">
                {result ? '1' : '0'}
              </p>
              <div className="mt-2 h-8 flex items-end gap-0.5">
                {[40, 65, 45, 80, 55, result ? 100 : 0].map((h, i) => (
                  <div key={i} className="w-1.5 bg-[#e5e7eb] rounded-full" style={{ height: `${h}%` }} />
                ))}
              </div>
            </div>
            <div className="p-6 sm:p-8 flex flex-col justify-center">
              <p className="text-sm font-medium text-[#111827] mb-1">Ready to create</p>
              <p className="text-caption mb-4">Start with a topic and generate a full blog post in one click.</p>
              <button
                type="button"
                onClick={() => { setActiveNav('create'); setResult(null); setTopic(''); }}
                className="inline-flex items-center justify-center gap-2 w-full sm:w-auto bg-[#1d4ed8] hover:bg-[#1e40af] text-white font-medium text-sm px-4 py-2.5 rounded-lg transition shadow-sm"
              >
                New blog post
                <ArrowIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        </section>

        {/* Quick action cards — 3 equal cards */}
        <section className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <QuickCard
            icon={<PenIcon className="w-5 h-5" />}
            accent="blue"
            title="Create blog"
            description="Generate a new post from a topic. We handle research, writing, and LinkedIn optimization."
            onClick={() => setActiveNav('create')}
          />
          <QuickCard
            icon={<DocIcon className="w-5 h-5" />}
            accent="amber"
            title="Recent posts"
            description="View and manage your generated posts. Download markdown or republish."
            onClick={() => setActiveNav('dashboard')}
          />
          <QuickCard
            icon={<BookIcon className="w-5 h-5" />}
            accent="gray"
            title="How it works"
            description="Learn about research agents, tone settings, and publishing to LinkedIn or WhatsApp."
          />
        </section>

        {/* Main content card — Create form or Result */}
        <section className="bg-white rounded-2xl border border-[#e5e7eb] shadow-sm overflow-hidden">
          {/* Optional info banner */}
          {!result && !generating && (
            <div className="bg-[#eff6ff] border-b border-[#bfdbfe] px-6 py-3 flex items-center justify-between gap-4">
              <p className="text-sm text-[#1e40af]">
                New: Generate a full blog with sources, then edit the LinkedIn post before publishing.
              </p>
              <button type="button" className="text-sm font-medium text-[#1d4ed8] hover:underline shrink-0">Learn more</button>
            </div>
          )}

          <div className="p-6 sm:p-8">
            {!result && !generating && (
              <div className="max-w-2xl">
                <h2 className="text-heading-2 mb-1">Create your post</h2>
                <p className="text-body mb-6">Enter a topic and choose tone and length. Generation usually takes 30–60 seconds.</p>
                <div className="space-y-5">
                  <div>
                    <label htmlFor="topic" className="block text-sm font-medium text-[#374151] mb-2">
                      Topic
                    </label>
                    <textarea
                      id="topic"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      placeholder="e.g. How zero-trust architecture reduces insider threat in 2025"
                      rows={4}
                      className="w-full rounded-xl border border-[#d1d5db] bg-white px-4 py-3 text-[#111827] placeholder-[#9ca3af] focus:outline-none focus:ring-2 focus:ring-[#1d4ed8] focus:border-[#1d4ed8] resize-y text-sm"
                    />
                  </div>
                  <div className="flex flex-wrap items-center gap-6">
                    <div>
                      <label className="block text-label mb-1.5">Tone</label>
                      <select
                        value={tone}
                        onChange={(e) => setTone(e.target.value as (typeof TONES)[number])}
                        className="rounded-lg border border-[#d1d5db] bg-white px-3 py-2 text-sm text-[#374151] focus:outline-none focus:ring-2 focus:ring-[#1d4ed8]"
                      >
                        {TONES.map((t) => (
                          <option key={t} value={t}>{t}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-label mb-1.5">Length</label>
                      <select
                        value={length}
                        onChange={(e) => setLength(e.target.value as (typeof LENGTHS)[number])}
                        className="rounded-lg border border-[#d1d5db] bg-white px-3 py-2 text-sm text-[#374151] focus:outline-none focus:ring-2 focus:ring-[#1d4ed8]"
                      >
                        {LENGTHS.map((l) => (
                          <option key={l} value={l}>{l}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div className="flex flex-col sm:flex-row sm:items-center gap-4 pt-2">
                    <button
                      type="button"
                      onClick={handleGenerate}
                      disabled={!topic.trim()}
                      className="inline-flex items-center justify-center gap-2 bg-[#1d4ed8] hover:bg-[#1e40af] disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium text-sm px-5 py-2.5 rounded-lg transition shadow-sm"
                    >
                      Generate blog post
                      <ArrowIcon className="w-4 h-4" />
                    </button>
                    <button
                      type="button"
                      onClick={() => setTopic(SAMPLE_TOPIC)}
                      className="text-sm text-[#6b7280] hover:text-[#111827] underline underline-offset-2"
                    >
                      Use sample topic
                    </button>
                  </div>
                </div>
              </div>
            )}

            {generating && (
              <div className="py-16 text-center">
                <div className="inline-flex flex-col items-center gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-[#eff6ff] flex items-center justify-center">
                    <div className="w-6 h-6 border-2 border-[#1d4ed8] border-t-transparent rounded-full animate-spin" />
                  </div>
                  <div>
                    <p className="font-semibold text-[#111827]">Generating your blog</p>
                    <p className="text-caption mt-1">Research → Write → Optimize for LinkedIn → Create thumbnail</p>
                  </div>
                </div>
              </div>
            )}

            {result && !generating && (
              <div className="flex flex-col lg:flex-row gap-8">
                <article className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-baseline justify-between gap-2 mb-5">
                    <h2 className="text-heading-2">{result.topic}</h2>
                    <p className="text-caption">
                      {wordCount} words
                      {result.sources?.length ? ` · ${result.sources.length} sources` : ''}
                    </p>
                  </div>
                  <div className="prose prose-sm max-w-none prose-headings:font-semibold prose-headings:text-[#111827] prose-p:text-[#4b5563] prose-li:text-[#4b5563]">
                    <MarkdownContent content={result.full_content} />
                  </div>
                  <div className="mt-6 pt-6 border-t border-[#e5e7eb]">
                    <button
                      type="button"
                      onClick={() => {
                        const blob = new Blob([result.full_content], { type: 'text/markdown' })
                        const a = document.createElement('a')
                        a.href = URL.createObjectURL(blob)
                        a.download = `${result.topic.replace(/\s+/g, '-').toLowerCase()}.md`
                        a.click()
                        URL.revokeObjectURL(a.href)
                      }}
                      className="text-sm font-medium text-[#6b7280] hover:text-[#111827] flex items-center gap-2"
                    >
                      <DownloadIcon className="w-4 h-4" />
                      Download as Markdown
                    </button>
                  </div>
                </article>

                <aside className="lg:w-[340px] shrink-0 space-y-6">
                  <div className="bg-[#f9fafb] rounded-xl border border-[#e5e7eb] overflow-hidden">
                    <div className="px-4 py-3 border-b border-[#e5e7eb]">
                      <p className="text-label">Cover image</p>
                    </div>
                    <div className="p-4">
                      {thumbnailUrl ? (
                        <img src={thumbnailUrl} alt="" className="w-full aspect-video object-cover rounded-lg border border-[#e5e7eb]" />
                      ) : (
                        <div className="w-full aspect-video rounded-lg border border-dashed border-[#d1d5db] flex items-center justify-center text-caption bg-white">
                          No thumbnail
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="bg-[#f9fafb] rounded-xl border border-[#e5e7eb] overflow-hidden">
                    <div className="px-4 py-3 border-b border-[#e5e7eb]">
                      <p className="text-label">LinkedIn post</p>
                      <p className="text-caption mt-0.5">Edit and publish</p>
                    </div>
                    <div className="p-4 space-y-4">
                      <textarea
                        value={linkedinPost}
                        onChange={(e) => setLinkedinPost(e.target.value)}
                        rows={8}
                        className="w-full rounded-lg border border-[#d1d5db] bg-white px-3 py-2.5 text-sm text-[#374151] placeholder-[#9ca3af] focus:outline-none focus:ring-2 focus:ring-[#1d4ed8] focus:border-[#1d4ed8] resize-y"
                      />
                      <p className={`text-xs font-mono text-right ${linkedinPost.length > 3000 ? 'text-red-600' : linkedinPost.length > 2500 ? 'text-amber-600' : 'text-[#9ca3af]'}`}>
                        {linkedinPost.length} / 3000
                      </p>
                      <div className="flex flex-col gap-2">
                        <button
                          type="button"
                          onClick={handleLinkedIn}
                          disabled={publishing !== null}
                          className="w-full bg-[#1d4ed8] hover:bg-[#1e40af] disabled:opacity-50 text-white font-medium py-2.5 rounded-lg text-sm transition"
                        >
                          {publishing === 'linkedin' ? 'Posting…' : 'Post to LinkedIn'}
                        </button>
                        <button
                          type="button"
                          onClick={handleWhatsApp}
                          disabled={publishing !== null}
                          className="w-full border border-[#d1d5db] bg-white hover:bg-[#f9fafb] text-[#374151] font-medium py-2.5 rounded-lg text-sm transition"
                        >
                          {publishing === 'whatsapp' ? 'Sending…' : 'Send via WhatsApp'}
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="bg-[#f9fafb] rounded-xl border border-[#e5e7eb] overflow-hidden">
                    <button
                      type="button"
                      onClick={() => setSummaryOpen((o) => !o)}
                      className="w-full px-4 py-3 flex items-center justify-between text-left"
                    >
                      <p className="text-label">Summary</p>
                      <ChevronIcon className={`w-4 h-4 text-[#9ca3af] transition ${summaryOpen ? 'rotate-180' : ''}`} />
                    </button>
                    {summaryOpen && (
                      <div className="px-4 pb-4 pt-0 border-t border-[#e5e7eb]">
                        <p className="text-body pt-3">{result.summary}</p>
                      </div>
                    )}
                  </div>
                </aside>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

function QuickCard({
  icon,
  accent,
  title,
  description,
  onClick,
}: {
  icon: React.ReactNode
  accent: 'blue' | 'amber' | 'gray'
  title: string
  description: string
  onClick?: () => void
}) {
  const borderClass =
    accent === 'blue' ? 'border-b-[#93c5fd]' : accent === 'amber' ? 'border-b-[#fcd34d]' : 'border-b-[#e5e7eb]'
  const iconBg =
    accent === 'blue' ? 'bg-[#eff6ff] text-[#1d4ed8]' : accent === 'amber' ? 'bg-[#fffbeb] text-[#d97706]' : 'bg-[#f3f4f6] text-[#6b7280]'
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full text-left bg-white rounded-2xl border border-[#e5e7eb] shadow-sm overflow-hidden p-6 hover:shadow transition border-b-4 ${borderClass} ${onClick ? 'cursor-pointer' : 'cursor-default opacity-90'}`}
    >
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4 ${iconBg}`}>
        {icon}
      </div>
      <h3 className="text-[1rem] font-semibold text-[#111827] mb-1.5">{title}</h3>
      <p className="text-caption leading-relaxed mb-4">{description}</p>
      {onClick && (
        <span className="inline-flex items-center text-[#6b7280] text-sm font-medium">
          Open
          <ArrowIcon className="w-4 h-4 ml-1" />
        </span>
      )}
    </button>
  )
}

function MarkdownContent({ content }: { content: string }) {
  const lines = content.split('\n')
  const elements: React.ReactNode[] = []
  let key = 0
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (line.startsWith('### ')) {
      elements.push(<h3 key={key++} className="text-base font-semibold text-[#111827] mt-6 mb-2">{line.slice(4)}</h3>)
    } else if (line.startsWith('## ')) {
      elements.push(<h2 key={key++} className="text-lg font-semibold text-[#111827] mt-8 mb-2 pb-2 border-b border-[#e5e7eb]">{line.slice(3)}</h2>)
    } else if (line.startsWith('# ')) {
      elements.push(<h1 key={key++} className="text-xl font-bold text-[#111827] mt-6 mb-2">{line.slice(2)}</h1>)
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      elements.push(<li key={key++} className="ml-4 list-disc text-[#4b5563]">{line.slice(2)}</li>)
    } else if (line.trim() === '') {
      elements.push(<div key={key++} className="h-2" />)
    } else {
      elements.push(<p key={key++} className="mb-2 text-[#4b5563]">{line}</p>)
    }
  }
  return <div className="space-y-1">{elements}</div>
}

function BoltIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  )
}

function ArrowIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
    </svg>
  )
}

function DownloadIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
  )
}

function ChevronIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
    </svg>
  )
}

function PenIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
    </svg>
  )
}

function DocIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  )
}

function BookIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
    </svg>
  )
}

function SettingsIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  )
}

export default App
