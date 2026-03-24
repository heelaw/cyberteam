import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui'
import { Button } from '@/components/ui'

export function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">设置</h1>
        <p className="text-muted-foreground">配置 CyberTeam Dashboard</p>
      </div>

      <div className="grid gap-6 max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle>通知设置</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">桌面通知</p>
                <p className="text-sm text-muted-foreground">启用浏览器桌面通知</p>
              </div>
              <Button variant="outline">启用</Button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">消息声音</p>
                <p className="text-sm text-muted-foreground">收到新消息时播放声音</p>
              </div>
              <Button variant="outline">启用</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>显示设置</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">深色模式</p>
                <p className="text-sm text-muted-foreground">切换深色/浅色主题</p>
              </div>
              <Button variant="outline">切换</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
