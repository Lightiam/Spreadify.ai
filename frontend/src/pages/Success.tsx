import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";

export default function Success() {
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    // Show success message
    toast({
      title: "Payment Successful!",
      description: "Thank you for subscribing to Spreadify. You can now start streaming!",
    });
  }, [toast]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-8 p-8">
        <div className="mx-auto w-24 h-24 rounded-full bg-green-100 flex items-center justify-center">
          <svg
            className="w-12 h-12 text-green-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>

        <h1 className="text-4xl font-bold">Payment Successful!</h1>
        
        <p className="text-xl text-muted-foreground max-w-md">
          Thank you for subscribing to Spreadify. You can now start streaming with all the premium features!
        </p>

        <div className="space-x-4">
          <Button onClick={() => navigate("/studio")} size="lg">
            Go to Studio
          </Button>
          <Button
            variant="outline"
            onClick={() => navigate("/pricing")}
            size="lg"
          >
            View Plans
          </Button>
        </div>
      </div>
    </div>
  );
}
