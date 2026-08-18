export interface SupportItem {
  name: string
  status: 'supported' | 'planned'
  note?: string
}

export interface SupportGroup {
  category: string
  items: SupportItem[]
}

export const compatibility: SupportGroup[] = [
  {
    category: 'Hosts',
    items: [
      { name: 'Codex', status: 'supported', note: 'Fully supported host' },
      { name: 'Claude', status: 'planned' },
      { name: 'Gemini', status: 'planned' },
    ],
  },
  {
    category: 'Languages',
    items: [
      { name: 'Python', status: 'supported' },
      { name: 'C++', status: 'planned' },
      { name: 'Java', status: 'planned' },
      { name: 'C#', status: 'planned' },
      { name: 'Rust', status: 'planned' },
    ],
  },
  {
    category: 'Version control',
    items: [
      { name: 'Git', status: 'supported' },
      { name: 'GitHub', status: 'supported' },
      { name: 'GitLab', status: 'planned' },
      { name: 'Bitbucket', status: 'planned' },
    ],
  },
  {
    category: 'Platforms',
    items: [
      { name: 'macOS', status: 'supported' },
      { name: 'Linux', status: 'planned' },
      { name: 'Windows', status: 'planned' },
    ],
  },
]
