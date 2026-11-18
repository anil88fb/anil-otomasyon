# Anıl Otomasyon

Anıl Otomasyon

## Claude becerileri

`.claude/skills/` klasöründe 88 beceri var. Claude Code bu depoda açıldığında bunları otomatik olarak tanır. Aynı beceriler `anil-otomasyon` eklentisi olarak Claude hesabına da yüklüdür (docx, pdf ve xlsx hariç; bunlar Claude'da yerleşik).

| Beceri | Kaynak |
|---|---|
| `ad-creative` | alirezarezvani/claude-skills |
| `agent-designer` | alirezarezvani/claude-skills |
| `algorithmic-art` | anthropics/skills |
| `assistant-coach` | alirezarezvani/claude-skills |
| `avoid-ai-writing` | wshobson/agents |
| `banner-design` | nextlevelbuilder/ui-ux-pro-max-skill |
| `bash-defensive-patterns` | wshobson/agents |
| `brainstorming` | obra/superpowers |
| `brand` | nextlevelbuilder/ui-ux-pro-max-skill |
| `browser-automation` | alirezarezvani/claude-skills |
| `business-name-fit` | alirezarezvani/claude-skills |
| `canvas-design` | anthropics/skills |
| `capture` | alirezarezvani/claude-skills |
| `competitive-ads-extractor` | ComposioHQ/awesome-claude-skills |
| `content-humanizer` | alirezarezvani/claude-skills |
| `content-production` | alirezarezvani/claude-skills |
| `copy-editing` | alirezarezvani/claude-skills |
| `copywriting` | alirezarezvani/claude-skills |
| `demo-video` | alirezarezvani/claude-skills |
| `dispatching-parallel-agents` | obra/superpowers |
| `docx` | anthropics/skills |
| `domain-name-brainstormer` | ComposioHQ/awesome-claude-skills |
| `eas-app-stores` | expo/skills |
| `executing-plans` | obra/superpowers |
| `expo-web-to-native` | expo/skills |
| `ffmpeg` | digitalsamba/claude-code-video-toolkit |
| `file-organizer` | ComposioHQ/awesome-claude-skills |
| `firecrawl-qa` | firecrawl/skills |
| `github-actions-templates` | wshobson/agents |
| `huggingface-best` | huggingface/skills |
| `huggingface-gradio` | huggingface/skills |
| `hyperframes` | calesthio/openmontage |
| `hyperframes-animation` | calesthio/openmontage |
| `hyperframes-cli` | calesthio/openmontage |
| `hyperframes-core` | calesthio/openmontage |
| `hyperframes-creative` | calesthio/openmontage |
| `hyperframes-media` | calesthio/openmontage |
| `hyperframes-registry` | calesthio/openmontage |
| `image-enhancer` | ComposioHQ/awesome-claude-skills |
| `interaction-design` | wshobson/agents |
| `lead-research-assistant` | ComposioHQ/awesome-claude-skills |
| `llm-cost-optimizer` | alirezarezvani/claude-skills |
| `local-seo-manager` | alirezarezvani/claude-skills |
| `manim-composer` | calesthio/openmontage |
| `marketing-context` | alirezarezvani/claude-skills |
| `mcp-builder` | anthropics/skills |
| `memory-engineering` | alirezarezvani/claude-skills |
| `mobile-release` | alirezarezvani/claude-skills |
| `modern-python` | trailofbits/skills |
| `moviepy` | digitalsamba/claude-code-video-toolkit |
| `music-to-video` | calesthio/openmontage |
| `nodejs-backend-patterns` | wshobson/agents |
| `notebooklm` | alirezarezvani/claude-skills |
| `parody-short` | digitalsamba/claude-code-video-toolkit |
| `pdf` | anthropics/skills |
| `prompt-engineering-patterns` | wshobson/agents |
| `pulse` | alirezarezvani/claude-skills |
| `python-background-jobs` | wshobson/agents |
| `raffle-winner-picker` | ComposioHQ/awesome-claude-skills |
| `remotion-captions` | remotion-dev/skills |
| `remotion-maps` | remotion-dev/skills |
| `remotion-markup` | remotion-dev/skills |
| `remotion-render` | remotion-dev/skills |
| `remotion-studio` | remotion-dev/skills |
| `responsive-design` | wshobson/agents |
| `saas-scaffolder` | alirezarezvani/claude-skills |
| `sast-configuration` | wshobson/agents |
| `semgrep` | trailofbits/skills |
| `seo-audit` | alirezarezvani/claude-skills |
| `skill-security-auditor` | alirezarezvani/claude-skills |
| `social-content` | alirezarezvani/claude-skills |
| `social-media-analyzer` | alirezarezvani/claude-skills |
| `social-media-manager` | alirezarezvani/claude-skills |
| `sql-database-assistant` | alirezarezvani/claude-skills |
| `stride-analysis-patterns` | wshobson/agents |
| `subagent-driven-development` | obra/superpowers |
| `systematic-debugging` | obra/superpowers |
| `test-driven-development` | obra/superpowers |
| `transformers-js` | huggingface/skills |
| `video-content-strategist` | alirezarezvani/claude-skills |
| `video-design` | digitalsamba/claude-code-video-toolkit |
| `video-downloader` | ComposioHQ/awesome-claude-skills |
| `webapp-testing` | anthropics/skills |
| `writing-plans` | obra/superpowers |
| `writing-skills` | obra/superpowers |
| `xlsx` | anthropics/skills |
| `youtube-full` | alirezarezvani/claude-skills |
| `youtube-stats` | digitalsamba/claude-code-video-toolkit |

## Notlar

- Her becerinin lisansı kendi kaynak deposundaki lisanstır. anthropics/skills içindeki docx, pdf ve xlsx kaynağı açık (source-available) ama açık kaynak değil; sadece kişisel kullanım içindir.
- calesthio/openmontage kaynaklı beceriler (HyperFrames ailesi, music-to-video, manim-composer) AGPL-3.0 lisanslıdır: kişisel kullanımda serbest, ama değiştirip başkalarına dağıtırsan ya da hizmet olarak sunarsan kaynak kodunu paylaşman gerekir.
- `assistant-coach` aslen `claude-coach` adındadır; beceri adlarında "claude" kelimesi kullanılamadığı için yeniden adlandırıldı.
- youtube-stats, video-design, parody-short ve moviepy becerilerinin kullandığı araç dosyaları, kaynak deponun ana klasöründen becerinin kendi `tools/` klasörüne kopyalandı.
- hyperframes-animation içindeki iki büyük örnek video (36 MB) hiçbir yerde kullanılmadığı için çıkarıldı.
- Remotion ticari kullanımda belirli büyüklüğün üzerindeki şirketler için ücretli lisans ister.
