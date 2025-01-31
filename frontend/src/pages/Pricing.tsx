import { Button } from "@/components/ui/button";
import { env } from "@/lib/env";
import { useNavigate } from "react-router-dom";
import { loadStripe } from "@stripe/stripe-js";

const stripePromise = loadStripe(env.VITE_STRIPE_PUBLIC_KEY);

const plans = [
  {
    name: "Basic",
    price: "Free",
    features: [
      "720p Streaming",
      "Up to 2 guests",
      "Basic overlays",
      "Stream to 1 platform",
      "4 hours per stream"
    ],
    priceId: null
  },
  {
    name: "Professional",
    price: "$25",
    period: "per month",
    features: [
      "1080p Streaming",
      "Up to 6 guests",
      "Custom overlays",
      "Stream to 3 platforms",
      "Unlimited streaming",
      "Recording storage",
      "Analytics"
    ],
    priceId: "price_H5ggYwtDq4fbrJ"
  },
  {
    name: "Business",
    price: "$49",
    period: "per month",
    features: [
      "4K Streaming",
      "Up to 10 guests",
      "Advanced overlays",
      "Stream to unlimited platforms",
      "Unlimited streaming",
      "Priority support",
      "White-label service",
      "Team management"
    ],
    priceId: "price_H5ggYwtDq4fbrK"
  }
];

export default function Pricing() {
  const navigate = useNavigate();

  const handleSubscribe = async (priceId: string | null) => {
    if (!priceId) {
      navigate("/login");
      return;
    }

    const stripe = await stripePromise;
    if (!stripe) return;

    try {
      const response = await fetch(`${env.VITE_API_URL}/stripe/create-checkout-session`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          priceId,
          successUrl: `${env.VITE_PUBLIC_URL}/success`,
          cancelUrl: `${env.VITE_PUBLIC_URL}/pricing`,
        }),
      });

      const session = await response.json();
      await stripe.redirectToCheckout({
        sessionId: session.id,
      });
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Choose Your Plan</h1>
          <p className="text-xl text-muted-foreground">
            Start streaming professionally with our flexible plans
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className="rounded-lg border p-8 flex flex-col justify-between"
            >
              <div>
                <h3 className="text-2xl font-bold">{plan.name}</h3>
                <div className="mt-4 flex items-baseline">
                  <span className="text-4xl font-extrabold">{plan.price}</span>
                  {plan.period && (
                    <span className="ml-2 text-muted-foreground">{plan.period}</span>
                  )}
                </div>
                <ul className="mt-6 space-y-4">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center">
                      <svg
                        className="h-5 w-5 text-green-500 mr-2"
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
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
              <Button
                className="mt-8 w-full"
                variant={plan.name === "Professional" ? "default" : "outline"}
                onClick={() => handleSubscribe(plan.priceId)}
              >
                {plan.price === "Free" ? "Get Started" : "Subscribe"}
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
