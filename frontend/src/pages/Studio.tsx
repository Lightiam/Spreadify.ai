import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { env } from "@/lib/env";

export default function Studio() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isConnected, setIsConnected] = useState(false);
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);

  useEffect(() => {
    // Check authentication and initialize WebSocket connection
    const token = localStorage.getItem("token");
    if (!token) {
      toast({
        variant: "destructive",
        title: "Authentication Error",
        description: "Please log in again.",
      });
      navigate('/login');
      return;
    }

    const ws = new WebSocket(`${env.VITE_WS_URL}/ws?token=${token}`);
    
    ws.onopen = () => {
      setIsConnected(true);
      toast({
        title: "Connected to Studio",
        description: "You can now start streaming.",
      });
    };

    ws.onclose = () => {
      setIsConnected(false);
      toast({
        variant: "destructive",
        title: "Connection Lost",
        description: "Please refresh the page to reconnect.",
      });
    };

    // Initialize camera and microphone
    async function setupMediaDevices() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        setLocalStream(stream);
      } catch (error) {
        console.error("Error accessing media devices:", error);
        toast({
          variant: "destructive",
          title: "Media Access Error",
          description: "Please ensure camera and microphone permissions are granted.",
        });
      }
    }

    setupMediaDevices();

    // Cleanup
    return () => {
      ws.close();
      if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
      }
    };
  }, [navigate, toast]);

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b p-4">
        <div className="container mx-auto flex justify-between items-center">
          <div className="text-xl font-bold">Spreadify Studio</div>
          <div className="flex items-center gap-4">
            <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm text-muted-foreground">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
            <Button variant="outline" size="sm">
              Settings
            </Button>
          </div>
        </div>
      </nav>

      <main className="container mx-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Preview Area */}
          <div className="lg:col-span-2 aspect-video bg-black rounded-lg relative">
            {localStream && (
              <video
                autoPlay
                muted
                playsInline
                className="w-full h-full object-cover rounded-lg"
                ref={(video) => {
                  if (video && localStream) {
                    video.srcObject = localStream;
                  }
                }}
              />
            )}
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2">
              <Button size="sm" variant="outline">
                <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24">
                  <path fill="none" stroke="currentColor" strokeWidth="2" d="M15 10l5-5-5-5"/>
                  <path fill="none" stroke="currentColor" strokeWidth="2" d="M20 5h-9a7 7 0 100 14h9"/>
                </svg>
                Share Screen
              </Button>
              <Button size="sm" variant="outline">
                <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24">
                  <path fill="none" stroke="currentColor" strokeWidth="2" d="M12 18.5L12 5.5"/>
                  <path fill="none" stroke="currentColor" strokeWidth="2" d="M5.5 12L18.5 12"/>
                </svg>
                Add Guest
              </Button>
            </div>
          </div>

          {/* Controls Area */}
          <div className="space-y-4">
            <div className="p-4 border rounded-lg">
              <h3 className="font-semibold mb-4">Stream Settings</h3>
              <div className="space-y-2">
                <Button className="w-full" variant="outline">
                  Connect YouTube
                </Button>
                <Button className="w-full" variant="outline">
                  Connect Facebook
                </Button>
                <Button className="w-full" variant="outline">
                  Connect Twitch
                </Button>
              </div>
            </div>

            <div className="p-4 border rounded-lg">
              <h3 className="font-semibold mb-4">Brand Settings</h3>
              <div className="space-y-2">
                <Button className="w-full" variant="outline">
                  Overlays
                </Button>
                <Button className="w-full" variant="outline">
                  Themes
                </Button>
              </div>
            </div>

            <Button className="w-full" variant="destructive">
              Go Live
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
