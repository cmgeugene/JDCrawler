import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { crawlSite } from "@/lib/api";
import { Play } from "lucide-react";

export function CrawlTrigger() {
    const [site, setSite] = useState("saramin");
    const [keyword, setKeyword] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const handleCrawl = async () => {
        if (!keyword) return;
        setIsLoading(true);
        try {
            await crawlSite(site, keyword);
            alert(`Crawling started for ${site} with keyword "${keyword}"`);
            setKeyword("");
        } catch (error) {
            console.error(error);
            alert(`Failed to start crawl: ${error instanceof Error ? error.message : "Unknown error"}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex items-center gap-2 p-4 border rounded-xl bg-card shadow-sm">
            <div className="w-[140px]">
                <Select
                    value={site}
                    onChange={(e) => setSite(e.target.value)}
                >
                    <option value="saramin">Saramin</option>
                    <option value="jobkorea">JobKorea</option>
                    <option value="wanted">Wanted</option>
                </Select>
            </div>
            <Input
                placeholder="Keyword (e.g. python)"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="max-w-[200px]"
            />
            <Button onClick={handleCrawl} disabled={isLoading || !keyword}>
                {isLoading ? (
                    <span className="animate-spin mr-2">⏳</span>
                ) : (
                    <Play className="mr-2 h-4 w-4" />
                )}
                Run Crawl
            </Button>
        </div>
    );
}
