export interface ButtonProps {
  label: string
  tone?: 'primary' | 'secondary'
}

export function Button(label: string, tone: ButtonProps['tone'] = 'primary') {
  return { label, tone }
}

export function Card(title: string, content: string) {
  return { title, content }
}
