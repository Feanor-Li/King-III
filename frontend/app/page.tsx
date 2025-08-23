"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Slider } from "@/components/ui/slider"
import {
  Upload,
  Camera,
  MessageCircle,
  Eye,
  Aperture,
  Sun,
  Send,
  RotateCcw,
  Sparkles,
  Target,
  Focus,
  Settings,
} from "lucide-react"

interface AnalysisResult {
  composition: {
    ruleOfThirds: number
    leadingLines: number
    symmetry: number
    framing: number
  }
  exposure: {
    brightness: number
    contrast: number
    highlights: number
    shadows: number
    iso: number
    aperture: number
    shutterSpeed: number
    whiteBalance: number
  }
  color: {
    saturation: number
    temperature: number
    vibrance: number
  }
  suggestions: string[]
  markers: Array<{
    id: string
    x: number
    y: number
    type: "focus" | "composition" | "exposure" | "highlight"
    label: string
    description: string
  }>
}

export default function SmartPhotographyApp() {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [chatMessages, setChatMessages] = useState<Array<{ type: "user" | "assistant"; content: string }>>([])
  const [currentMessage, setCurrentMessage] = useState("")
  const [activeMarker, setActiveMarker] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setUploadedImage(e.target?.result as string)
        simulateAnalysis()
      }
      reader.readAsDataURL(file)
    }
  }

  const simulateAnalysis = () => {
    setIsAnalyzing(true)
    setTimeout(() => {
      setAnalysisResult({
        composition: {
          ruleOfThirds: 78,
          leadingLines: 65,
          symmetry: 45,
          framing: 82,
        },
        exposure: {
          brightness: 72,
          contrast: 68,
          highlights: 85,
          shadows: 55,
          iso: 200,
          aperture: 2.8,
          shutterSpeed: 125,
          whiteBalance: 5600,
        },
        color: {
          saturation: 75,
          temperature: 6200,
          vibrance: 70,
        },
        suggestions: [
          "Great use of rule of thirds, but try moving the subject slightly to the left",
          "Overall exposure is good, consider lowering highlights to preserve more detail",
          "Color saturation is well balanced, you might add a bit more warmth",
        ],
        markers: [
          {
            id: "focus-1",
            x: 35,
            y: 40,
            type: "focus",
            label: "Main Subject",
            description: "Primary focus point - well positioned using rule of thirds",
          },
          {
            id: "composition-1",
            x: 65,
            y: 25,
            type: "composition",
            label: "Leading Line",
            description: "Strong leading line draws attention to subject",
          },
          {
            id: "exposure-1",
            x: 80,
            y: 15,
            type: "exposure",
            label: "Highlight Area",
            description: "Potential overexposure - consider reducing highlights",
          },
          {
            id: "highlight-1",
            x: 20,
            y: 70,
            type: "highlight",
            label: "Shadow Detail",
            description: "Good shadow retention with detail preservation",
          },
          {
            id: "composition-2",
            x: 50,
            y: 60,
            type: "composition",
            label: "Balance Point",
            description: "Visual weight balance creates harmony",
          },
        ],
      })
      setIsAnalyzing(false)
    }, 3000)
  }

  const handleExposureChange = (parameter: string, value: number[]) => {
    if (analysisResult) {
      setAnalysisResult({
        ...analysisResult,
        exposure: {
          ...analysisResult.exposure,
          [parameter]: value[0],
        },
      })
    }
  }

  const handleSendMessage = () => {
    if (currentMessage.trim()) {
      setChatMessages((prev) => [...prev, { type: "user", content: currentMessage }])
      setTimeout(() => {
        setChatMessages((prev) => [
          ...prev,
          {
            type: "assistant",
            content:
              "I understand you want to adjust the composition. Based on your feedback, I recommend setting ISO to 200, aperture to f/2.8, and shutter speed to 1/125s. This will give you better depth of field control.",
          },
        ])
      }, 1000)
      setCurrentMessage("")
    }
  }

  const handleConfigureCamera = () => {
    if (analysisResult) {
      alert(
        `Configuring iPhone camera settings...\n\nISO: ${analysisResult.exposure.iso}\nAperture: f/${analysisResult.exposure.aperture}\nShutter: 1/${analysisResult.exposure.shutterSpeed}s\nWhite Balance: ${analysisResult.exposure.whiteBalance}K`,
      )
    }
  }

  const exposureParameters = [
    { key: "brightness", label: "Brightness", min: 0, max: 100, step: 1, unit: "%" },
    { key: "contrast", label: "Contrast", min: 0, max: 100, step: 1, unit: "%" },
    { key: "highlights", label: "Highlights", min: 0, max: 100, step: 1, unit: "%" },
    { key: "shadows", label: "Shadows", min: 0, max: 100, step: 1, unit: "%" },
    { key: "iso", label: "ISO", min: 100, max: 3200, step: 100, unit: "" },
    { key: "aperture", label: "Aperture", min: 1.4, max: 16, step: 0.1, unit: "f/" },
    { key: "shutterSpeed", label: "Shutter Speed", min: 30, max: 4000, step: 10, unit: "1/s" },
    { key: "whiteBalance", label: "White Balance", min: 2500, max: 10000, step: 100, unit: "K" },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-card/20 to-secondary/10">
      <style jsx>{`
        @keyframes scanLine {
          0% { transform: translateY(-100%); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateY(100vh); opacity: 0; }
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 0.4; }
          50% { opacity: 1; }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        
        @keyframes particleFloat {
          0% { transform: translate(0, 0) rotate(0deg); opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { transform: translate(100px, -100px) rotate(360deg); opacity: 0; }
        }
        
        @keyframes markerPulse {
          0%, 100% { transform: scale(1); opacity: 0.8; }
          50% { transform: scale(1.2); opacity: 1; }
        }
        
        @keyframes spotlightGlow {
          0%, 100% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.3); }
          50% { box-shadow: 0 0 40px rgba(59, 130, 246, 0.6); }
        }
        
        .scan-line {
          animation: scanLine 2s ease-in-out infinite;
        }
        
        .pulse-glow {
          animation: pulse 2s ease-in-out infinite;
        }
        
        .float-animation {
          animation: float 3s ease-in-out infinite;
        }
        
        .shimmer-effect {
          background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
          background-size: 200% 100%;
          animation: shimmer 2s infinite;
        }
        
        .particle {
          animation: particleFloat 4s ease-out infinite;
        }
        
        .analysis-grid {
          position: relative;
          background-image: 
            linear-gradient(rgba(59, 130, 246, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.1) 1px, transparent 1px);
          background-size: 20px 20px;
        }
        
        .marker-pulse {
          animation: markerPulse 2s ease-in-out infinite;
        }
        
        .spotlight-glow {
          animation: spotlightGlow 3s ease-in-out infinite;
        }
      `}</style>

      <header className="border-b border-border/50 bg-card/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-gradient-to-br from-primary to-accent rounded-xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                <Camera className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">Real Pro Photographer</h1>
                <p className="text-sm text-muted-foreground">AI-powered camera configuration</p>
              </div>
            </div>
            <Badge
              variant="secondary"
              className="gap-2 px-4 py-2 bg-gradient-to-r from-accent/20 to-primary/20 border-accent/30"
            >
              <Sparkles className="w-4 h-4" />
              Pro Mode
            </Badge>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {!uploadedImage ? (
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <div className="w-20 h-20 bg-gradient-to-br from-primary to-accent rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl">
                <Camera className="w-10 h-10 text-primary-foreground" />
              </div>
              <h2 className="text-4xl font-bold text-foreground mb-4">Shoot Like a Pro</h2>
              <p className="text-xl text-muted-foreground">
                Upload any photo and get perfect camera settings for your iPhone
              </p>
            </div>

            <Card className="border-2 border-dashed border-primary/30 bg-gradient-to-br from-card to-secondary/30 hover:border-primary/50 transition-colors">
              <CardContent className="flex flex-col items-center justify-center py-16">
                <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mb-6">
                  <Upload className="w-8 h-8 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-3 text-foreground">Upload Your Reference Photo</h3>
                <p className="text-muted-foreground text-center mb-8 max-w-md leading-relaxed">
                  Drop any photo here and we'll analyze it to configure your iPhone camera automatically
                </p>
                <Button onClick={() => fileInputRef.current?.click()} size="lg" className="px-8 py-3 text-lg">
                  <Upload className="w-5 h-5 mr-2" />
                  Choose Photo
                </Button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="grid lg:grid-cols-2 gap-8 h-[calc(100vh-12rem)]">
            {/* Left side: Photo display area */}
            <div className="space-y-6">
              <Card className="h-full bg-gradient-to-br from-card to-secondary/20 border-primary/20 relative overflow-hidden">
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-3 text-xl">
                      <Eye className="w-6 h-6 text-primary" />
                      Reference Photo
                    </CardTitle>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => fileInputRef.current?.click()}
                      className="border-primary/30 hover:bg-primary/10"
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Re-upload
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="flex-1 flex items-center justify-center p-6 relative">
                  {isAnalyzing && (
                    <>
                      {/* Scanning line effect */}
                      <div className="absolute inset-0 z-10 pointer-events-none">
                        <div className="absolute w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent scan-line"></div>
                      </div>

                      {/* Grid overlay */}
                      <div className="absolute inset-0 analysis-grid opacity-30 z-10"></div>

                      {/* Floating particles */}
                      <div className="absolute inset-0 z-10 pointer-events-none">
                        {[...Array(8)].map((_, i) => (
                          <div
                            key={i}
                            className="absolute w-2 h-2 bg-primary rounded-full particle"
                            style={{
                              left: `${Math.random() * 100}%`,
                              top: `${Math.random() * 100}%`,
                              animationDelay: `${i * 0.5}s`,
                            }}
                          ></div>
                        ))}
                      </div>

                      {/* Corner analysis indicators */}
                      <div className="absolute top-4 left-4 w-8 h-8 border-l-2 border-t-2 border-primary pulse-glow z-10"></div>
                      <div className="absolute top-4 right-4 w-8 h-8 border-r-2 border-t-2 border-primary pulse-glow z-10"></div>
                      <div className="absolute bottom-4 left-4 w-8 h-8 border-l-2 border-b-2 border-primary pulse-glow z-10"></div>
                      <div className="absolute bottom-4 right-4 w-8 h-8 border-r-2 border-b-2 border-primary pulse-glow z-10"></div>
                    </>
                  )}

                  <div className="relative w-full h-full max-h-[600px] rounded-2xl overflow-hidden shadow-2xl">
                    <img
                      src={uploadedImage || "/placeholder.svg"}
                      alt="Reference photo"
                      className={`w-full h-full object-contain bg-gradient-to-br from-muted/20 to-secondary/20 transition-all duration-500 ${
                        isAnalyzing ? "brightness-110 contrast-110" : ""
                      }`}
                    />
                    {isAnalyzing && <div className="absolute inset-0 shimmer-effect"></div>}

                    {analysisResult?.markers && (
                      <div className="absolute inset-0 pointer-events-none">
                        {analysisResult.markers.map((marker, index) => {
                          const markerColors = {
                            focus: "bg-blue-500 border-blue-400",
                            composition: "bg-green-500 border-green-400",
                            exposure: "bg-yellow-500 border-yellow-400",
                            highlight: "bg-purple-500 border-purple-400",
                          }

                          const markerIcons = {
                            focus: Focus,
                            composition: Target,
                            exposure: Sun,
                            highlight: Sparkles,
                          }

                          const IconComponent = markerIcons[marker.type]

                          return (
                            <div
                              key={marker.id}
                              className={`absolute transform -translate-x-1/2 -translate-y-1/2 pointer-events-auto cursor-pointer transition-all duration-300 ${
                                activeMarker === marker.id ? "scale-125 z-20" : "z-10"
                              }`}
                              style={{
                                left: `${marker.x}%`,
                                top: `${marker.y}%`,
                                animationDelay: `${index * 200}ms`,
                              }}
                              onMouseEnter={() => setActiveMarker(marker.id)}
                              onMouseLeave={() => setActiveMarker(null)}
                            >
                              {/* Spotlight effect for active marker */}
                              {activeMarker === marker.id && (
                                <div className="absolute inset-0 w-32 h-32 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/10 spotlight-glow"></div>
                              )}

                              {/* Marker dot */}
                              <div
                                className={`w-6 h-6 rounded-full border-2 ${markerColors[marker.type]} marker-pulse flex items-center justify-center shadow-lg`}
                              >
                                <IconComponent className="w-3 h-3 text-white" />
                              </div>

                              {/* Marker label */}
                              {activeMarker === marker.id && (
                                <div className="absolute top-8 left-1/2 transform -translate-x-1/2 bg-black/80 text-white px-3 py-2 rounded-lg text-xs whitespace-nowrap shadow-xl animate-in fade-in zoom-in duration-200">
                                  <div className="font-semibold">{marker.label}</div>
                                  <div className="text-gray-300 text-xs mt-1">{marker.description}</div>
                                  <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-black/80 rotate-45"></div>
                                </div>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right side: Analysis and chat area */}
            <div className="space-y-6 overflow-y-auto">
              {isAnalyzing ? (
                <Card className="bg-gradient-to-br from-card to-secondary/20 relative overflow-hidden">
                  <CardContent className="flex flex-col items-center justify-center py-16">
                    <div className="relative mb-6">
                      <div className="w-16 h-16 border-4 border-primary/30 rounded-full"></div>
                      <div className="absolute inset-0 w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                      <div
                        className="absolute inset-2 w-12 h-12 border-2 border-accent/50 rounded-full animate-spin"
                        style={{ animationDirection: "reverse", animationDuration: "1s" }}
                      ></div>

                      {[...Array(6)].map((_, i) => (
                        <Sparkles
                          key={i}
                          className="absolute w-4 h-4 text-primary float-animation"
                          style={{
                            left: `${20 + Math.cos((i * 60 * Math.PI) / 180) * 40}px`,
                            top: `${20 + Math.sin((i * 60 * Math.PI) / 180) * 40}px`,
                            animationDelay: `${i * 0.3}s`,
                          }}
                        />
                      ))}
                    </div>

                    <h3 className="text-xl font-semibold mb-2 text-foreground">AI is analyzing...</h3>
                    <p className="text-muted-foreground text-center mb-4">
                      Analyzing photo composition, exposure, and color parameters
                    </p>

                    <div className="w-full max-w-md space-y-2">
                      <div className="flex justify-between text-sm text-muted-foreground">
                        <span>Composition Analysis</span>
                        <span className="pulse-glow">●</span>
                      </div>
                      <div className="flex justify-between text-sm text-muted-foreground">
                        <span>Exposure Detection</span>
                        <span className="pulse-glow" style={{ animationDelay: "0.5s" }}>
                          ●
                        </span>
                      </div>
                      <div className="flex justify-between text-sm text-muted-foreground">
                        <span>Color Analysis</span>
                        <span className="pulse-glow" style={{ animationDelay: "1s" }}>
                          ●
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ) : analysisResult ? (
                <>
                  <Card className="bg-gradient-to-br from-amber-500/10 via-card to-amber-600/5 border-amber-400/30 shadow-lg animate-in slide-in-from-right duration-500">
                    <CardContent className="p-6">
                      <Button
                        onClick={handleConfigureCamera}
                        className="w-full h-16 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white shadow-xl hover:shadow-2xl transform hover:scale-[1.02] transition-all duration-300 text-lg font-semibold"
                        size="lg"
                      >
                        <div className="flex items-center justify-center gap-4">
                          <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                            <Aperture className="w-6 h-6" />
                          </div>
                          <div className="text-left">
                            <div className="text-lg font-bold">Apply to iPhone Camera</div>
                            <div className="text-sm opacity-90">Configure settings automatically</div>
                          </div>
                          <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                        </div>
                      </Button>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-card to-secondary/20 border-primary/20 animate-in slide-in-from-right duration-500">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-3 text-lg">
                        <Settings className="w-5 h-5 text-primary" />
                        Exposure Parameters
                      </CardTitle>
                      <CardDescription>
                        Adjust camera settings in real-time to match your reference photo
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="grid gap-6">
                        {exposureParameters.map((param, index) => {
                          const currentValue =
                            analysisResult.exposure[param.key as keyof typeof analysisResult.exposure]
                          return (
                            <div
                              key={param.key}
                              className="animate-in slide-in-from-left duration-500 space-y-3"
                              style={{ animationDelay: `${index * 100}ms` }}
                            >
                              <div className="flex justify-between items-center">
                                <Label className="text-sm font-medium text-foreground">{param.label}</Label>
                                <div className="flex items-center gap-2">
                                  <span className="text-sm font-semibold text-primary min-w-[60px] text-right">
                                    {param.unit === "f/"
                                      ? `f/${currentValue}`
                                      : param.unit === "1/s"
                                        ? `1/${currentValue}s`
                                        : `${currentValue}${param.unit}`}
                                  </span>
                                </div>
                              </div>
                              <Slider
                                value={[currentValue]}
                                onValueChange={(value) => handleExposureChange(param.key, value)}
                                min={param.min}
                                max={param.max}
                                step={param.step}
                                className="w-full"
                              />
                              <div className="flex justify-between text-xs text-muted-foreground">
                                <span>
                                  {param.unit === "f/"
                                    ? `f/${param.min}`
                                    : param.unit === "1/s"
                                      ? `1/${param.min}s`
                                      : `${param.min}${param.unit}`}
                                </span>
                                <span>
                                  {param.unit === "f/"
                                    ? `f/${param.max}`
                                    : param.unit === "1/s"
                                      ? `1/${param.max}s`
                                      : `${param.max}${param.unit}`}
                                </span>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </CardContent>
                  </Card>

                  {/* AI Suggestions */}
                  <Card className="bg-gradient-to-br from-card to-secondary/20 border-primary/20 animate-in slide-in-from-right duration-500 delay-400">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-3 text-lg">
                        <Sparkles className="w-5 h-5 text-primary" />
                        Smart Suggestions
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {analysisResult.suggestions.map((suggestion, index) => (
                        <div
                          key={index}
                          className="flex gap-3 p-4 bg-gradient-to-r from-secondary/40 to-primary/10 rounded-xl border border-primary/20 animate-in slide-in-from-left duration-500"
                          style={{ animationDelay: `${600 + index * 150}ms` }}
                        >
                          <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0 pulse-glow"></div>
                          <p className="text-sm leading-relaxed">{suggestion}</p>
                        </div>
                      ))}
                    </CardContent>
                  </Card>

                  {/* Chat Interface */}
                  <Card className="bg-gradient-to-br from-card to-secondary/20 border-primary/20 animate-in slide-in-from-right duration-500 delay-600">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-3 text-lg">
                        <MessageCircle className="w-5 h-5 text-primary" />
                        Smart Chat Adjustment
                      </CardTitle>
                      <CardDescription className="text-muted-foreground">
                        Tell me what specific aspects you'd like to adjust, and I'll optimize the camera parameters for
                        you
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="h-48 overflow-y-auto space-y-3 p-4 bg-gradient-to-br from-muted/20 to-secondary/20 rounded-xl border border-primary/10">
                        {chatMessages.length === 0 ? (
                          <div className="text-center text-muted-foreground py-8">
                            <MessageCircle className="w-8 h-8 mx-auto mb-3 opacity-50" />
                            <p className="text-sm">Start a conversation to adjust shooting parameters</p>
                          </div>
                        ) : (
                          chatMessages.map((message, index) => (
                            <div
                              key={index}
                              className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
                            >
                              <div
                                className={`max-w-[80%] p-3 rounded-xl shadow-sm ${
                                  message.type === "user"
                                    ? "bg-gradient-to-r from-primary to-accent text-primary-foreground"
                                    : "bg-card border border-primary/20"
                                }`}
                              >
                                <p className="text-sm leading-relaxed">{message.content}</p>
                              </div>
                            </div>
                          ))
                        )}
                      </div>

                      <div className="flex gap-3">
                        <Textarea
                          placeholder="e.g., I want a shallower depth of field, or make the photo warmer..."
                          value={currentMessage}
                          onChange={(e) => setCurrentMessage(e.target.value)}
                          className="flex-1 bg-gradient-to-br from-secondary/20 to-primary/5 border-primary/20"
                          rows={2}
                        />
                        <Button
                          onClick={handleSendMessage}
                          disabled={!currentMessage.trim()}
                          size="lg"
                          className="px-4"
                        >
                          <Send className="w-4 h-4" />
                        </Button>
                      </div>

                      <div className="flex flex-wrap gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setCurrentMessage("I want a shallower depth of field")}
                          className="border-primary/30 hover:bg-primary/10"
                        >
                          Shallow DOF
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setCurrentMessage("The photo needs warmer tones")}
                          className="border-primary/30 hover:bg-primary/10"
                        >
                          Warm Tones
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setCurrentMessage("Enhance the photo contrast")}
                          className="border-primary/30 hover:bg-primary/10"
                        >
                          High Contrast
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setCurrentMessage("Re-analyze composition")}
                          className="border-primary/30 hover:bg-primary/10"
                        >
                          <RotateCcw className="w-3 h-3 mr-1" />
                          Re-analyze
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </>
              ) : null}
            </div>
          </div>
        )}

        <input ref={fileInputRef} type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
      </div>
    </div>
  )
}
