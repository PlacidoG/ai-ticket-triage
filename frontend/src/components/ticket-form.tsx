"use client";

import { useState } from "react";
import { Paperclip, Send, Loader2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { createTicket } from "@/lib/api";

interface FormErrors {
  title?: string;
  description?: string;
  email?: string;
  phone?: string;
}

export function TicketForm() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [contactMethod, setContactMethod] = useState<"email" | "sms">("email");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});

  const descriptionLength = description.length;
  const isShortDescription = descriptionLength > 0 && descriptionLength < 20;

  function validate(): boolean {
    const newErrors: FormErrors = {};

    if (!title.trim()) {
      newErrors.title = "Title is required";
    } else if (title.trim().length < 5) {
      newErrors.title = "Title should be at least 5 characters for accurate AI classification";
    }

    if (!description.trim()) {
      newErrors.description = "Description is required";
    } else if (description.trim().length < 10) {
      newErrors.description = "Please provide more detail so the AI can classify accurately";
    }

    if (contactMethod === "email") {
      if (!email.trim()) {
        newErrors.email = "Email is required so IT can follow up with you";
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        newErrors.email = "Please enter a valid email address";
      }
    } else {
      if (!phone.trim()) {
        newErrors.phone = "Phone number is required for SMS contact";
      } else if (phone.replace(/\D/g, "").length < 10) {
        newErrors.phone = "Please enter a valid 10-digit phone number";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit() {
    if (!validate()) return;

    setIsSubmitting(true);
    setErrors({});

    try {
      const fullName = [firstName.trim(), lastName.trim()].filter(Boolean).join(" ");
      const contactInfo = contactMethod === "email" ? email.trim() : `sms:${phone.trim()}`;

      const ticket = await createTicket({
        title: title.trim(),
        description: description.trim(),
        submitter_email: fullName ? `${fullName} <${contactInfo}>` : contactInfo,
      });

      toast.success("Ticket submitted successfully", {
        description: "AI is analyzing your ticket now. Classification will appear in a few seconds.",
        action: {
          label: "View Ticket",
          onClick: () => {
            window.location.href = `/tickets/${ticket.id}`;
          },
        },
        duration: 8000,
      });

      // Reset form
      setTitle("");
      setDescription("");
      setFirstName("");
      setLastName("");
      setEmail("");
      setPhone("");
    } catch (error) {
      toast.error("Failed to submit ticket", {
        description: error instanceof Error ? error.message : "Please try again",
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <Card className="border-2">
        <CardHeader>
          <CardTitle>New Support Ticket</CardTitle>
          <CardDescription>
            Describe your issue clearly. Our AI will automatically classify
            your ticket by severity and category, and suggest an initial response.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Title */}
          <div className="space-y-2">
            <label htmlFor="title" className="text-sm font-medium leading-none">
              Title <span className="text-destructive">*</span>
            </label>
            <Input
              id="title"
              placeholder="e.g., Can't log into VPN from home office"
              value={title}
              onChange={(e) => {
                setTitle(e.target.value);
                if (errors.title) setErrors({ ...errors, title: undefined });
              }}
              className={`border-2 ${errors.title ? "border-destructive" : ""}`}
              disabled={isSubmitting}
            />
            {errors.title && (
              <p className="text-sm text-destructive">{errors.title}</p>
            )}
            <p className="text-xs text-muted-foreground">
              A clear, specific title helps the AI classify your ticket accurately
            </p>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <label htmlFor="description" className="text-sm font-medium leading-none">
              Description <span className="text-destructive">*</span>
            </label>
            <Textarea
              id="description"
              placeholder="Describe your issue in detail. Include error messages, steps to reproduce, and any urgency or deadlines."
              value={description}
              onChange={(e) => {
                setDescription(e.target.value);
                if (errors.description)
                  setErrors({ ...errors, description: undefined });
              }}
              className={`min-h-[150px] border-2 ${errors.description ? "border-destructive" : ""}`}
              disabled={isSubmitting}
            />
            <div className="flex items-center justify-between">
              <div>
                {errors.description && (
                  <p className="text-sm text-destructive">
                    {errors.description}
                  </p>
                )}
                {isShortDescription && !errors.description && (
                  <p className="text-sm text-yellow-600 dark:text-yellow-500">
                    Short descriptions may reduce AI classification accuracy
                  </p>
                )}
              </div>
              <span
                className={`text-xs ${
                  isShortDescription
                    ? "text-yellow-600 dark:text-yellow-500"
                    : "text-muted-foreground"
                }`}
              >
                {descriptionLength} characters
              </span>
            </div>
          </div>

          <Separator />

          {/* File Attachment Placeholder */}
          <div className="space-y-2">
            <label className="text-sm font-medium leading-none text-muted-foreground">
              Attachments
              <span className="ml-1 text-xs">(coming soon)</span>
            </label>
            <div className="flex items-center gap-2 rounded-md border-2 border-dashed p-4 text-sm text-muted-foreground">
              <Paperclip className="h-4 w-4" />
              <span>
                File attachments will be supported in a future release.
                For now, please paste error messages or screenshots in the
                description.
              </span>
            </div>
          </div>

          <Separator />

          {/* Preferred Contact Method */}
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">
                Preferred Contact Method <span className="text-destructive">*</span>
              </label>
              <div className="flex gap-3">
                <Button
                  type="button"
                  variant={contactMethod === "email" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setContactMethod("email")}
                  disabled={isSubmitting}
                  className="border-2"
                >
                  Email
                </Button>
                <Button
                  type="button"
                  variant={contactMethod === "sms" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setContactMethod("sms")}
                  disabled={isSubmitting}
                  className="border-2"
                >
                  SMS / Text
                </Button>
              </div>
            </div>

            {/* Name Fields (optional) */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="firstName" className="text-sm font-medium leading-none">
                  First Name
                  <span className="ml-1 text-xs text-muted-foreground">(optional)</span>
                </label>
                <Input
                  id="firstName"
                  placeholder="Jane"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="border-2"
                  disabled={isSubmitting}
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="lastName" className="text-sm font-medium leading-none">
                  Last Name
                  <span className="ml-1 text-xs text-muted-foreground">(optional)</span>
                </label>
                <Input
                  id="lastName"
                  placeholder="Doe"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="border-2"
                  disabled={isSubmitting}
                />
              </div>
            </div>
            <p className="text-xs text-muted-foreground">
              Adding your name helps IT staff communicate with you more personally
            </p>

            {/* Email or Phone based on contact method */}
            {contactMethod === "email" ? (
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium leading-none">
                  Work Email <span className="text-destructive">*</span>
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (errors.email) setErrors({ ...errors, email: undefined });
                  }}
                  className={`border-2 ${errors.email ? "border-destructive" : ""}`}
                  disabled={isSubmitting}
                />
                {errors.email && (
                  <p className="text-sm text-destructive">{errors.email}</p>
                )}
              </div>
            ) : (
              <div className="space-y-2">
                <label htmlFor="phone" className="text-sm font-medium leading-none">
                  Phone Number <span className="text-destructive">*</span>
                </label>
                <Input
                  id="phone"
                  type="tel"
                  placeholder="(555) 123-4567"
                  value={phone}
                  onChange={(e) => {
                    setPhone(e.target.value);
                    if (errors.phone) setErrors({ ...errors, phone: undefined });
                  }}
                  className={`border-2 ${errors.phone ? "border-destructive" : ""}`}
                  disabled={isSubmitting}
                />
                {errors.phone && (
                  <p className="text-sm text-destructive">{errors.phone}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  SMS notifications coming in a future release. Your number
                  will be saved for when this feature launches.
                </p>
              </div>
            )}
          </div>

          <Separator />

          {/* Submit Button */}
          <div className="flex justify-end">
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="min-w-[140px]"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="mr-2 h-4 w-4" />
                  Submit Ticket
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}