import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getProfile, updateProfile } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, Save, User, Code, Briefcase, Target, ShieldAlert, Plus, Trash2 } from "lucide-react";
import type { TechSkill } from "@/types";

export default function Profile() {
  const queryClient = useQueryClient();
  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: getProfile,
  });

  const [skills, setSkills] = useState<TechSkill[]>([]);
  const [experienceYears, setExperienceYears] = useState(0);
  const [interests, setInterests] = useState("");
  const [excludes, setExcludes] = useState("");

  useEffect(() => {
    if (profile) {
      setSkills(profile.tech_stack || []);
      setExperienceYears(profile.experience_years);
      setInterests(profile.interest_keywords.join(", "));
      setExcludes(profile.exclude_keywords.join(", "));
    }
  }, [profile]);

  const mutation = useMutation({
    mutationFn: updateProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      alert("Profile updated successfully!");
    },
  });

  const addSkill = () => {
    setSkills([...skills, { name: "", level: "Intermediate", description: "" }]);
  };

  const removeSkill = (index: number) => {
    setSkills(skills.filter((_, i) => i !== index));
  };

  const updateSkill = (index: number, field: keyof TechSkill, value: string) => {
    const newSkills = [...skills];
    newSkills[index] = { ...newSkills[index], [field]: value };
    setSkills(newSkills);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      tech_stack: skills.filter(s => s.name.trim()),
      experience_years: experienceYears,
      interest_keywords: interests.split(",").map(s => s.trim()).filter(Boolean),
      exclude_keywords: excludes.split(",").map(s => s.trim()).filter(Boolean),
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 p-4">
      <div className="flex items-center gap-4 border-b border-border pb-6">
        <div className="p-3 bg-primary/10 rounded-xl">
          <User className="h-8 w-8 text-primary" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">User Profile</h1>
          <p className="text-muted-foreground font-mono text-sm uppercase">Detailed Skills & Experience</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Experience Section */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-primary uppercase font-mono">
            <Briefcase className="h-4 w-4" />
            <span>Career Info</span>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-xs text-muted-foreground font-mono">YEARS_OF_EXP</label>
              <Input
                type="number"
                min="0"
                value={experienceYears}
                onChange={(e) => setExperienceYears(parseInt(e.target.value) || 0)}
                className="bg-card font-mono"
              />
            </div>
          </div>
        </div>

        {/* Tech Stack Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-semibold text-primary uppercase font-mono">
              <Code className="h-4 w-4" />
              <span>Technical Skills (Proficiency)</span>
            </div>
            <Button type="button" variant="outline" size="sm" onClick={addSkill} className="h-8 gap-1">
              <Plus className="h-3 w-3" /> Add Skill
            </Button>
          </div>
          
          <div className="space-y-3">
            {skills.map((skill, index) => (
              <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-3 p-4 rounded-lg border border-border/50 bg-muted/20 animate-in slide-in-from-left-2 duration-200">
                <div className="md:col-span-1">
                  <Input
                    placeholder="Skill Name (e.g. Python)"
                    value={skill.name}
                    onChange={(e) => updateSkill(index, "name", e.target.value)}
                    className="h-9 text-sm"
                  />
                </div>
                <div className="md:col-span-1">
                  <select
                    className="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={skill.level}
                    onChange={(e) => updateSkill(index, "level", e.target.value)}
                  >
                    <option value="Beginner">Beginner (초급)</option>
                    <option value="Intermediate">Intermediate (중급)</option>
                    <option value="Advanced">Advanced (고급)</option>
                    <option value="Expert">Expert (전문가)</option>
                  </select>
                </div>
                <div className="md:col-span-1.5 flex-1">
                  <Input
                    placeholder="Details (e.g. Can distinguish variables/funcs)"
                    value={skill.description || ""}
                    onChange={(e) => updateSkill(index, "description", e.target.value)}
                    className="h-9 text-sm"
                  />
                </div>
                <div className="flex justify-end">
                  <Button type="button" variant="ghost" size="icon" onClick={() => removeSkill(index)} className="h-9 w-9 text-muted-foreground hover:text-destructive">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
            {skills.length === 0 && (
              <div className="text-center py-8 border border-dashed rounded-lg text-muted-foreground text-sm font-mono">
                No skills added yet. Add your tech stack to improve AI analysis.
              </div>
            )}
          </div>
        </div>

        {/* Keywords Section */}
        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-primary uppercase font-mono">
              <Target className="h-4 w-4" />
              <span>Interest Keywords</span>
            </div>
            <Input
              placeholder="AI Agent, LLM, RAG..."
              value={interests}
              onChange={(e) => setInterests(e.target.value)}
              className="bg-card font-mono"
            />
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-primary uppercase font-mono">
              <ShieldAlert className="h-4 w-4" />
              <span>Exclude Keywords</span>
            </div>
            <Input
              placeholder="Marketing, Sales, Design..."
              value={excludes}
              onChange={(e) => setExcludes(e.target.value)}
              className="bg-card font-mono"
            />
          </div>
        </div>

        <div className="pt-6 border-t border-border flex justify-end">
          <Button 
            type="submit" 
            disabled={mutation.isPending}
            className="min-w-[150px] gap-2"
          >
            {mutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            Save Profile
          </Button>
        </div>
      </form>
    </div>
  );
}