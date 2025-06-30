import Sidebar from '../components/Sidebar'
export default function Page(){
  return (
    <div className="flex">
      <Sidebar />
      <div className="p-4">multi page</div>
    </div>
  )
}
