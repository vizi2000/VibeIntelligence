import { useState } from 'react';
import { 
  Moon, 
  Sun, 
  Zap, 
  Heart, 
  Bell,
  Save
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import toast from 'react-hot-toast';

export default function Settings() {
  const [settings, setSettings] = useState({
    theme: 'light',
    vibeLevel: 'high',
    notifications: true,
    autoScan: true,
    scanInterval: 'daily',
    ecoMode: true,
    adhdfriendly: true,
    language: 'en'
  });

  const handleSave = () => {
    localStorage.setItem('zenithSettings', JSON.stringify(settings));
    toast.success('Settings saved successfully! 🎉');
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-muted-foreground">
          Customize your Zenith Coder experience
        </p>
      </div>

      <div className="space-y-6">
        {/* Appearance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sun className="w-5 h-5" />
              Appearance
            </CardTitle>
            <CardDescription>
              Customize how Zenith Coder looks
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Theme</p>
                <p className="text-sm text-muted-foreground">Choose your preferred theme</p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant={settings.theme === 'light' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSettings({ ...settings, theme: 'light' })}
                >
                  <Sun className="w-4 h-4 mr-1" />
                  Light
                </Button>
                <Button
                  variant={settings.theme === 'dark' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSettings({ ...settings, theme: 'dark' })}
                >
                  <Moon className="w-4 h-4 mr-1" />
                  Dark
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Vibecoding */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="w-5 h-5 text-pink-500" />
              Vibecoding Settings
            </CardTitle>
            <CardDescription>
              Adjust your vibe and wellness preferences
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Vibe Level</p>
                <p className="text-sm text-muted-foreground">Set your default vibe intensity</p>
              </div>
              <select
                value={settings.vibeLevel}
                onChange={(e) => setSettings({ ...settings, vibeLevel: e.target.value })}
                className="px-3 py-1 border rounded-md"
              >
                <option value="zen">Zen Mode</option>
                <option value="medium">Balanced</option>
                <option value="high">High Energy</option>
                <option value="peak">Peak Flow</option>
              </select>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">ADHD-Friendly Mode</p>
                <p className="text-sm text-muted-foreground">Enable features for better focus</p>
              </div>
              <Button
                variant={settings.adhdfriendly ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSettings({ ...settings, adhdfriendly: !settings.adhdfriendly })}
              >
                {settings.adhdfriendly ? 'Enabled' : 'Disabled'}
              </Button>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Eco Mode</p>
                <p className="text-sm text-muted-foreground">Optimize for sustainability</p>
              </div>
              <Button
                variant={settings.ecoMode ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSettings({ ...settings, ecoMode: !settings.ecoMode })}
              >
                {settings.ecoMode ? 'Enabled' : 'Disabled'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Automation */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-500" />
              Automation
            </CardTitle>
            <CardDescription>
              Configure automatic features
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Auto Scan</p>
                <p className="text-sm text-muted-foreground">Automatically scan for new projects</p>
              </div>
              <Button
                variant={settings.autoScan ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSettings({ ...settings, autoScan: !settings.autoScan })}
              >
                {settings.autoScan ? 'Enabled' : 'Disabled'}
              </Button>
            </div>

            {settings.autoScan && (
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Scan Interval</p>
                  <p className="text-sm text-muted-foreground">How often to scan</p>
                </div>
                <select
                  value={settings.scanInterval}
                  onChange={(e) => setSettings({ ...settings, scanInterval: e.target.value })}
                  className="px-3 py-1 border rounded-md"
                >
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="w-5 h-5" />
              Notifications
            </CardTitle>
            <CardDescription>
              Manage your notification preferences
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Enable Notifications</p>
                <p className="text-sm text-muted-foreground">Get updates about your projects</p>
              </div>
              <Button
                variant={settings.notifications ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSettings({ ...settings, notifications: !settings.notifications })}
              >
                {settings.notifications ? 'Enabled' : 'Disabled'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button onClick={handleSave} size="lg">
            <Save className="w-4 h-4 mr-2" />
            Save Settings
          </Button>
        </div>
      </div>
    </div>
  );
}