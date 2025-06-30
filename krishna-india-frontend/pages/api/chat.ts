import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const backend = process.env.NEXT_PUBLIC_BACKEND_URL + '/chat'
  const response = await fetch(backend, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req.body)
  })
  const data = await response.json()
  res.status(response.status).json(data)
}
