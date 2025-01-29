import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 dark:focus-visible:ring-zinc-300",
  {
    variants: {
      variant: {
        default:
          "bg-brand-600 text-white shadow hover:bg-brand-700 transition-colors",
        destructive:
          "bg-red-500 text-white shadow-sm hover:bg-red-600 transition-colors",
        outline:
          "border border-brand-200 bg-white text-brand-700 shadow-sm hover:bg-brand-50 hover:border-brand-300 transition-colors",
        secondary:
          "bg-brand-100 text-brand-700 shadow-sm hover:bg-brand-200 transition-colors",
        ghost: 
          "text-brand-600 hover:bg-brand-50 hover:text-brand-700 transition-colors",
        link: 
          "text-brand-600 underline-offset-4 hover:text-brand-700 hover:underline transition-colors",
        brand:
          "bg-brand-600 text-white shadow-sm hover:bg-brand-700 focus:ring-2 focus:ring-brand-200 transition-colors",
      },
      size: {
        default: "h-10 px-4 py-2 text-sm",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-11 rounded-md px-8 text-base",
        xl: "h-12 rounded-md px-10 text-lg",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
