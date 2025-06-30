import type { NextApiRequest, NextApiResponse } from 'next'

export const config = {
  api: {
    bodyParser: false,
  },
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { message, session_id } = req.query
  const backendUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL}/stream?message=${encodeURIComponent(String(message))}&session_id=${session_id}`
  const backendRes = await fetch(backendUrl)

  res.status(backendRes.status)
  backendRes.body?.pipe(res)
}
