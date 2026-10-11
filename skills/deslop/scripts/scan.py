#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import re
import sys

LEVELS = {"weak": 1, "medium": 2, "strong": 3}
PROSE_SUFFIXES = {"", ".md", ".markdown", ".mdx", ".txt", ".rst", ".adoc", ".org", ".tex", ".html", ".htm"}
COMMENT = re.compile(r"^\s*(?:#(?!!)|//|/\*|\*(?!\*)|--\s|<!--|;;)\s?(.*)$")
TRAILING_COMMENT = re.compile(r"(?:\s{2}#(?![#!{\[])|\s//(?!/))\s?(.*)$")
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
URL = re.compile(r"https?://\S+")
WORD = re.compile(r"[\w'’-]+")
EMOJI = "\U0001F300-\U0001FAFF☀-➿⭐⭕"
KO_CLAUSE = re.compile(r"(?:[하되있없했됐겠았었였주오]고|[가-힣](?:며|지만|면서|아서|어서|해서|는데|은데|므로|니까))(,?)\s")

RULES = []


def rule(scope, level, rule_id, pattern, hint, flags=re.IGNORECASE):
    RULES.append((scope, level, rule_id, re.compile(pattern, flags), hint))


# Scopes: raw = line with inline code removed, URLs kept; prose = prose lines and comment text;
# markup = prose files only; comment = code comments only; code = code lines; pair = previous + current code line.
rule("raw", "strong", "chat-citation-residue",
     r"contentReference\[oaicite:\d+\]|\boai_citation\b|\bturn\d+(?:search|news|file|image|view)\d+\b"
     r"|utm_source=(?:chatgpt\.com|openai)|\[cite: ?\d+(?:, ?\d+)*\]|【\d+†[^】]*】|\[attached_file:\d+\]"
     r"|\bgrok_card\b|:::writing\{|\[span_\d+\]\((?:start|end)_span\)",
     "chatbot citation residue; remove it and cite the real source if there is one")
rule("raw", "medium", "git-assistant-trailer",
     r"Co-Authored-By:\s*(?:Claude|ChatGPT|Copilot|Cursor|Gemini|Codex|Devin)|noreply@anthropic\.com"
     r"|Generated with \[?(?:Claude|ChatGPT|Cursor|Codex|Copilot)|🤖 Generated",
     "assistant trailer; keep it only if the project requires AI disclosure")

rule("prose", "strong", "chat-placeholder",
     r"\[(?:Your|Insert|Recipient|Company|Author|Client|Product)\b[^\]\n]{0,40}\]|\bINSERT_[A-Z_]+\b"
     r"|\bPASTE_[A-Z_]+_HERE\b|\b20\d\d-XX-XX\b|\[(?:회사명|이름|날짜|제품명|고객명|담당자)[^\]\n]{0,20}\]",
     "unfilled placeholder; ask for the real value")
rule("prose", "strong", "en-ai-self-reference",
     r"\bas an AI(?: language)? model\b|\bas a large language model\b|\bI (?:do not|don't) have personal "
     r"(?:opinions|experiences|feelings)\b|\bas of my (?:last )?(?:knowledge|training) (?:update|cut-?off)\b",
     "assistant self-reference; delete it or state the real limit plainly")
rule("prose", "strong", "en-chat-opener",
     r"^\s*(?:Certainly|Sure|Absolutely|Of course)[!,.]\s+(?:Here|I)\b|\bGreat question\b"
     r"|\bYou're absolutely right\b|\bWhat a (?:great|fantastic|wonderful) (?:question|idea)\b"
     r"|\bI'd be (?:happy|glad) to help\b",
     "chat opener or flattery; delete it")
rule("prose", "strong", "en-chat-closer",
     r"\bI hope (?:this|that) (?:helps|finds you well|clarifies)\b|\bLet me know if (?:you|there)\b"
     r"|\bWould you like me to\b|\bFeel free to (?:reach out|ask|let me know)\b",
     "chat closer addressed to the prompter; delete it")
rule("prose", "strong", "en-testament",
     r"\b(?:stands?|serves?|stood|served) as an? (?:testament|reminder|beacon)\b|\ba testament to\b",
     "inflated significance; delete it or show the consequence")
rule("prose", "strong", "en-pivotal-role",
     r"\bplay(?:s|ed|ing)? an? (?:pivotal|crucial|vital|key|significant|instrumental|critical) role\b",
     "inflated significance; say what it actually does")
rule("prose", "strong", "en-tapestry",
     r"\b(?:rich|vibrant|intricate|complex|diverse) tapestry\b|\btapestry of\b",
     "stock metaphor; name the actual parts")
rule("prose", "strong", "en-template-opener",
     r"\bin today's (?:fast-paced|digital|ever-changing|modern|rapidly evolving|interconnected) "
     r"(?:world|age|landscape|era)\b|\bin (?:the|an) ever-(?:evolving|changing)\b|\bin a world where\b"
     r"|\b(?:let's|let us) (?:dive|delve)\b|\bdelv(?:e|es|ed|ing) (?:into|deeper)\b",
     "template opener; start with the first real claim")
rule("prose", "strong", "en-legacy",
     r"\b(?:enduring|lasting) legacy\b|\bindelible mark\b|\bsetting the stage for\b|\bevolving landscape\b"
     r"|\bmark(?:s|ed|ing)? an? (?:pivotal|significant|key|major) (?:moment|shift|turning point|milestone)\b"
     r"|\breflects? broader trends\b",
     "inflated significance; delete it or give the evidence")
rule("prose", "strong", "en-knowledge-disclaimer",
     r"\bwhile specific details (?:are|remain) (?:limited|scarce)\b|\bnot widely (?:documented|available|disclosed)\b"
     r"|\bbased on (?:the )?available information\b",
     "knowledge disclaimer; find the fact or leave the topic out")
rule("prose", "strong", "en-future-formula",
     r"\bthe future (?:looks|remains|is) (?:bright|promising)\b|\bdespite (?:these|its|the(?:se)?) challenges\b",
     "challenges-and-future formula; name the specific problem and drop the upbeat tag")
rule("prose", "medium", "en-negative-parallelism",
     r"\b(?:it|this|that|they)(?:'s| is| was| are|'re)(?: not|n't) (?:just |only |merely |about )?[^.!?;\n]{1,60}"
     r"[,;:—–]\s*(?:it|this|that|they)(?:'s| is| was| are|'re)\b|\b(?:is|are|was|were)(?:n't| not) (?:just|only"
     r"|merely|simply) [^.!?;\n]{1,60}[,;:—–]\s*(?:it|this|that|they)(?:'s| is| was| are|'re)\b"
     r"|\bnot (?:just|only|merely) (?!that\b)"
     r"[^.!?\n]{1,80}?,? but(?: also)?\b|\bno [a-z]+, no [a-z]+(?:, no [a-z]+)?[,.—–]\s*just\b"
     r"|\bnot because [^.\n]{1,60}, but because\b",
     "negative parallelism; state the positive claim, keep a contrast only if a reader holds the other view")
rule("prose", "medium", "en-ing-tail",
     r", (?:highlighting|underscoring|emphasizing|showcasing|reflecting|symbolizing|signaling|ensuring|fostering"
     r"|cementing|solidifying|contributing to|paving the way|underlining)\b",
     "evaluative -ing tail; delete it or make it a sentence with evidence")
rule("prose", "medium", "en-significance-verb",
     r"\b(?:underscor|highlight|emphasiz)(?:es|ed|ing) (?:the|its|their) (?:importance|significance|need|role)\b",
     "asserted significance; say what the evidence shows instead")
rule("prose", "medium", "en-serves-as",
     r"\b(?:serves|stands|functions|acts) as (?:a|an|the) (?!testament|reminder|beacon)",
     "avoided copula; use is or has")
rule("prose", "medium", "en-important-to-note",
     r"\bit(?:'s| is) (?:important|crucial|essential|worth|vital) (?:to note|noting|to remember|to mention"
     r"|mentioning)\b|\bworth noting\b",
     "didactic frame; delete the frame and keep the claim")
rule("prose", "medium", "en-signposting",
     r"\b(?:let's|let us) (?:explore|unpack|break (?:it|this|that) down|take a (?:closer |deeper )?look)\b"
     r"|\bin this (?:section|article|post|guide),? (?:we|I) (?:will|'ll)\b",
     "signposting; delete it and start with the content")
rule("prose", "medium", "en-staged-reveal",
     r"\bhere's (?:the thing|the kicker|the catch|the truth|what you need to know)\b"
     r"|\bthe (?:result|answer|catch|kicker|best part|twist)\?",
     "staged reveal; state the point")
rule("prose", "medium", "en-summary-closer",
     r"^\s*(?:in conclusion|in summary|to sum up|to summarize|ultimately|in essence)[,:]",
     "summary closer; end on the last new fact instead of restating")
rule("prose", "medium", "en-puffery",
     r"\bnestled\b|\bin the heart of\b|\bboasts (?:a|an|over|more|some)\b|\bbreathtaking\b"
     r"|\brich (?:heritage|history|culture)\b|\bdiverse (?:array|range) of\b|\bworld-class\b|\bcutting-edge\b"
     r"|\bgame[- ]changer\b|\bunlock (?:the|your) (?:full )?potential\b|\bto the next level\b"
     r"|\bcommitment to (?:excellence|quality|innovation)\b",
     "promotional wording; replace it with the fact it stands for")
rule("prose", "medium", "en-vague-attribution",
     r"\b(?:experts|observers|critics|scholars|analysts|industry reports) (?:argue|say|note|believe|suggest"
     r"|agree|have (?:noted|cited|argued))\b|\bstudies (?:show|suggest|have shown)\b"
     r"|\bit is (?:widely|generally) (?:believed|accepted|recognized)\b",
     "vague attribution; name the source from the original or cut the claim")
rule("prose", "medium", "en-hedge-stack",
     r"\b(?:may|might|could) (?:potentially|possibly|perhaps|arguably)\b|\b(?:potentially|possibly) (?:could|may|might)\b"
     r"|\bit could be argued\b",
     "stacked hedge; keep one hedge on the uncertain part")
rule("prose", "medium", "en-upbeat-vague",
     r"\bthe possibilities are endless\b|\ba beacon of (?:hope|innovation)\b|\bonly time will tell\b"
     r"|\bexciting times? ahead\b",
     "upbeat vagueness; delete it")
rule("prose", "medium", "en-process-talk",
     r"\bensuring (?:clarity|consistency|readability) and (?:flow|coherence)\b|\bpreserving the original (?:meaning|intent)\b",
     "editing-process talk left in the text; delete it")
rule("prose", "medium", "git-vague-change",
     r"\b(?:enhance|improve|update)[sd]?\b[^.\n]{0,40}\b(?:functionality|code quality|robustness|maintainability"
     r"|user experience)\b|^\s*This (?:PR|pull request|commit|change) (?:introduces|adds|implements|enhances|aims to)\b"
     r"|\bAll \d+ tests (?:pass|passing|passed)\b|\bcomprehensive (?:tests?|test suite|test coverage|documentation"
     r"|error handling)\b|\b(?:Initially|At first),? (?:I|we) (?:tried|attempted)\b",
     "vague change description; say what changed and why")
rule("prose", "weak", "en-vocabulary",
     r"\b(?:delv\w*|tapestr\w*|testament|intricat\w*|interplay|pivotal|showcas\w*"
     r"|meticulous\w*|garner\w*|bolster\w*|realm|multifaceted|nuanced|commendable|groundbreaking|invaluable"
     r"|noteworthy|burgeoning|seamless\w*|vibrant|enduring|foster\w*|leverag\w*|robust|crucial|embark\w*"
     r"|unwavering|amidst|resonat\w*|holistic|paramount|transformative|empower\w*|streamlin\w*|harness\w*"
     r"|navigat\w*|landscape)\b",
     "watch-list word; counts only in a cluster, and the fix is the fact it covers, not a synonym")
rule("prose", "weak", "en-additive-opener",
     r"^\s*(?:Additionally|Moreover|Furthermore|Notably|Importantly),",
     "additive opener; join the sentence to the previous one or drop the connective")
rule("prose", "weak", "arrow-in-prose", r"\s[→⇒➡]\s", "arrow in running prose; use a verb")

rule("prose", "strong", "ko-chat-opener",
     r"^\s*(?:물론(?:입니다|이죠|이에요|이지요)|좋은\s?질문(?:입니다|이에요|이네요)|훌륭한\s?질문)"
     r"|아래와\s?같이\s?정리해\s?드리",
     "챗봇 서두; 지운다")
rule("prose", "strong", "ko-chat-closer",
     r"도움이\s?(?:되셨|되었|됐)(?:기를|으면|길)|궁금한\s?(?:점|사항)이?\s?(?:있으시면|있으면|있다면)"
     r"|원하시면\s[^.!?\n]{0,40}(?:드릴까요|드릴게요|해\s?드릴)",
     "챗봇 맺음말; 지운다 (고객 공지의 문의 안내는 정상)")
rule("prose", "strong", "ko-sycophancy",
     r"핵심을\s?(?:정확히\s?)?(?:찌르|찔렀|짚었|꿰뚫)|(?:정말|아주|매우|참)\s?(?:좋은|훌륭한|날카로운|예리한)\s?"
     r"(?:질문|지적|통찰)|통찰력\s?있는\s?(?:분석|질문|지적)|충분히\s?이해합니다",
     "아첨이나 가짜 공감; 지운다")
rule("prose", "strong", "ko-antithesis",
     r"단순(?:히|한|하게)\s[^.!?\n]{1,40}?아니(?:라|고|다|며|에요|야)|단순(?:히|한)\s[^.!?\n]{1,40}?아닙니다"
     r"|단순한\s[^.!?\n]{1,20}[을를]\s?넘어|[이가]\s?아닙니다\.\s*[^.!?\n]{1,40}(?:입니다|이다|예요)\.",
     "부정 대조 공식; B만 말하고 실제 반론이 있을 때만 대조를 남긴다")
rule("prose", "strong", "ko-translationese-strong",
     r"함에\s?있어(?:서)?|에\s?다름\s?아니|의\s?그것(?:보다|과|와|은|는|이|을)",
     "강한 번역투; 자연스러운 한국어 구조로 다시 쓴다")
rule("prose", "medium", "ko-meta-intro",
     r"(?:이번|오늘|이)\s?(?:글|포스팅|시간|섹션)에서는|(?:살펴|알아)\s?(?:보겠|보도록|봅시다|볼까요)"
     r"|지금까지\s[^.!?\n]{0,20}(?:살펴|알아)\s?(?:보았|봤)",
     "메타 도입이나 요약; 지우고 본론으로 시작한다")
rule("prose", "medium", "ko-conclusion-marker",
     r"(?:^|[.!?]\s+)(?:결론적으로|요약하자면|요약하면|정리하자면|종합하면|종합하자면|궁극적으로"
     r"|결론부터\s?(?:말씀드리|말하)(?:면|자면))",
     "결론 표지; 앞 내용을 되풀이하는 문단이면 지운다")
rule("prose", "medium", "ko-cleft",
     r"(?:것|점)[이은]\s?(?:중요|필수|핵심)(?:합니다|하다|해요|하죠|적입니다|입니다|이다)"
     r"|(?:핵심|관건|요점|중요한\s?것|필요한\s?것)[은는]\s[^.!?\n]{1,60}(?:입니다|이다|라는\s?점|다는\s?점)",
     "분열문; 주장을 바로 쓴다")
rule("prose", "medium", "ko-cliche",
     r"시사하는\s?(?:바|점)[가이]?\s?(?:크|많)|주목할\s?(?:만한|만하|만합)|새로운\s?(?:지평|패러다임)"
     r"|(?:발판|토대|초석|교두보)[을를]\s?(?:마련|놓|다지)|게임\s?체인저|판도를\s?(?:바꾸|바꿀|바꿔|뒤집)"
     r"|무한한\s?가능성|행보가\s?기대|(?:핵심적인|필수적인|중요한)\s?(?:역할|요소)",
     "상투적 평가나 은유; 무엇이 가능해졌는지, 실제로 하는 일을 쓴다")
rule("prose", "medium", "ko-hedge",
     r"(?:라고|다고)\s?(?:할|볼)\s?수\s?있(?:습니다|다|어요)|수\s?있을\s?것으로\s?(?:보|예상|기대)",
     "헤징 겹침; 불확실한 부분에 한 번만 남긴다")
rule("prose", "medium", "ko-translationese",
     r"(?:능력|경쟁력|가능성|장점|특징|특성|의미|잠재력|권한|역량)[을를]\s?(?:가지고|갖고)\s?있"
     r"|(?:회의|시간|모임|대화|휴식)[을를]\s?(?:가지|가졌|가져|갖)|되어(?:지|진|졌|집)"
     r"|(?:보여|쓰여|불려|믿겨)(?:지|진|졌|집)|[을를]\s?필요로\s?(?:하|합|한|했)"
     r"|가장\s[^.!?\n]{1,20}\s?(?:중|가운데)\s?하나|[을를]\s?가능하게\s?(?:합|하|한|해)"
     r"|(?:단축|향상|증가|감소|발전|개선|강화|변화)\s?시(?:키|켜|킨|킵|켰)|(?:으로|로)부터의",
     "번역투; 원문 의미를 지키며 한국어 구조로 다시 쓴다")
rule("prose", "medium", "ko-conjunction-comma",
     r"(?:^|[.!?]\s+)(?:그리고|그러나|하지만|그런데|그러므로|따라서|또한|즉|게다가|더욱이|특히|나아가|결국|이처럼"
     r"|반면|한편),",
     "접속부사 뒤 쉼표; 쉼표를 지운다")
rule("prose", "medium", "ko-rhetorical",
     r"까요\?\s*(?:그|바로|답|정답|이유|비결)|(?:보면|보는\s?건)\s?어떨까요\?"
     r"|(?:하나만|한\s?가지)\s?(?:짚고|바로잡고)\s?(?:가자|갈게|가겠)|선을\s?(?:하나\s?)?긋고",
     "자문자답이나 교사·반박 말투; 내용을 바로 쓴다")
rule("prose", "medium", "ko-serial-and", r"[가-힣]+,\s?[가-힣]+,\s?그리고\s[가-힣]+",
     "영어식 세 항목 나열; 'A와 B, C'로 쓰거나 실제 항목 수에 맞춘다")
rule("prose", "medium", "ko-em-dash", "[가-힣]—[가-힣]",
     "붙여 쓴 em dash; 쉼표, 괄호, 문장 분리로 바꾼다")
rule("prose", "weak", "ko-vocabulary",
     r"(?:혁신적|획기적|압도적|차별화된|최적화된|원활(?:한|하게)|효과적(?:으로|인)|성공적(?:으로|인)|다양한)",
     "빈 수식어; 문단마다 나올 때만 문제다. 그 말이 가리던 사실을 쓴다")
rule("prose", "weak", "ko-additive-opener",
     r"(?:^|[.!?]\s+)(?:또한|게다가|더욱이|아울러|나아가|뿐만\s?아니라|이를\s?통해|이처럼|이에\s?따라)\s",
     "문두 접속사; 문단에 세 번 넘게 나오면 연결어미로 잇는다")

rule("markup", "strong", "md-emoji-lead", rf"^\s*(?:#{{1,6}}\s+|[-*+•]\s+|\d+[.)]\s+)?[{EMOJI}]",
     "emoji bullet or heading; remove unless the medium is casual or already uses them")
rule("markup", "strong", "md-bold-leak", r"[.,!?)\"'”’」』]\*\*[가-힣]",
     "닫는 ** 앞이 문장부호라 렌더링되지 않는다; 굵게를 지우거나 문장부호를 밖으로 뺀다")
rule("markup", "medium", "md-bold-label", r"^\s*(?:[-*+•]|\d+[.)])\s+\*\*[^*\n]{1,60}\*\*",
     "bold-label bullet; write the list plainly or as a paragraph")
rule("markup", "medium", "md-closing-heading",
     r"^#{1,6}\s+(?:Conclusion|Summary|Final Thoughts|Key Takeaways|TL;?DR|In Summary|결론|마무리|요약"
     r"|핵심\s?요약|핵심\s?정리|정리하며)\s*$",
     "closing heading; on a short piece, drop the heading and any restating paragraph")
rule("markup", "weak", "md-colon-heading", r"^#{1,6}\s+[^:\n]{1,30}:\s+\S",
     "colon heading; fine in docs, a tell in essays and posts")

rule("comment", "strong", "comment-step", r"^(?:Step\s*\d+\b|\d+\s?단계\s?[:.])",
     "narrating step comment; delete unless it mirrors a spec")
rule("comment", "strong", "comment-request-echo",
     r"\b(?:as requested|per (?:your|the user'?s?) (?:request|feedback|instructions?)|as you (?:asked|suggested))\b"
     r"|요청(?:하신|에\s?따라|대로)|말씀하신\s?대로",
     "comment addressed to the requester; delete it")
rule("comment", "strong", "comment-stub",
     r"\bIn a (?:real|production)(?:[- ]world)? (?:implementation|application|scenario|app|system)\b"
     r"|\bfor (?:demo|demonstration|simplicity)(?: purposes)?\b|\bsimplified (?:version|implementation)\b"
     r"|\byou (?:can|could|may) (?:extend|replace|customi[sz]e) (?:this|it)\b|\bspecial[- ]?cased? for (?:the )?tests?\b"
     r"|\bplaceholder (?:implementation|logic|value)\b",
     "stub or prompt leakage; finish the code or remove the note")
rule("comment", "medium", "comment-change-note",
     r"^(?:Updated|Changed|Fixed|Added|Removed|Modified|Refactored|Moved|Replaced|NEW|UPDATED|FIXED|CHANGED)\b"
     r"|^Now (?:uses|using|handles|supports|returns|calls)\b"
     r"|^(?:수정|추가|변경|개선|삭제)(?:됨|함)?\s?[:：]|(?:추가|수정|변경|개선|삭제)(?:했습니다|하였습니다|됨|함)\.?$",
     "comment narrating the edit; history belongs in git, keep only a real constraint", 0)
rule("comment", "medium", "comment-enhanced",
     r"\b(?:Enhanced|Improved|Robust|Comprehensive|Optimized|Proper)\s+(?:error handling|version|implementation"
     r"|logic|validation|logging|handling)\b",
     "self-praising comment; delete it")
rule("comment", "medium", "comment-emoji", rf"[{EMOJI}]", "emoji in a code comment; remove it")
rule("comment", "weak", "comment-what",
     r"^(?:Initiali[sz]e|Create|Define|Declare|Import|Set|Get|Return|Call|Increment|Loop (?:through|over)"
     r"|Iterate (?:through|over)|Check if)\b(?:\s+(?:the|a|an|all|new))?(?:\s+[\w.()]+){0,4}\s*\.?$",
     "comment that may restate the next line; delete it if it does")

rule("code", "medium", "code-type-escape",
     r"\bas any\b|\bas unknown as\b|<any>|:\s*any\b(?=\s*[,;)=>\]|]|\s*$)|@ts-ignore|@ts-expect-error"
     r"|#\s*type:\s*ignore|#\s*pyright:\s*ignore|\bcast\(\s*Any\b|eslint-disable|//\s*nolint|@SuppressWarnings",
     "type or lint escape; fix the type, or keep it with a one-line reason", 0)
rule("code", "medium", "code-swallowed-error",
     r"^\s*except\s*:|^\s*except\s+\(?\s*(?:Exception|BaseException)\b[^:\n]*:\s*(?:pass|\.\.\.|return(?: None"
     r"| \[\]| \{\}| \"\"| ''| False)?)\s*(?:#.*)?$"
     r"|catch\s*(?:\(\s*\w*\s*\))?\s*\{\s*\}|\.catch\(\s*\(\s*\w*\s*\)\s*=>\s*(?:null|undefined|\{\s*\}|\[\s*\]|void 0)\s*\)",
     "swallowed error; let it propagate unless this is a trust boundary or the file's idiom", 0)
rule("pair", "medium", "code-swallowed-error",
     r"^\s*except(?:\s+\(?\s*(?:Exception|BaseException)\b[^:\n]*)?\s*:\s*\n\s*(?:pass|continue"
     r"|return(?: None| \[\]| \{\}| \"\"| ''| False)?)\s*$",
     "swallowed error; let it propagate unless this is a trust boundary or the file's idiom", 0)
rule("pair", "medium", "code-rethrow-only",
     r"^\s*except(?:\s+\(?\s*(?:Exception|BaseException)\b[^:\n]*)?\s*:\s*\n\s*raise\s*$",
     "catch that only rethrows; delete the try", 0)
rule("code", "medium", "code-emoji-string", rf"([\"'`])[^\"'`\n]*?[{EMOJI}][^\"'`\n]*?\1",
     "emoji in a string; remove it unless the UI or CLI already uses emoji", 0)
rule("code", "medium", "code-stub", r"\bthrow new Error\(\s*[\"']Not implemented|\btodo!\(",
     "unfinished stub; finish or remove it", 0)
rule("code", "weak", "code-stub", r"\braise NotImplementedError\b|\bunimplemented!\(",
     "possible stub; fine in an abstract method, otherwise finish or remove it", 0)
rule("code", "medium", "code-test-special-case",
     r"NODE_ENV\s*===?\s*[\"']test[\"']|\bif\b[^\n]*\b(?:TESTING|is_test|IS_TEST)\b",
     "test-only branch in production code; remove it and fix the real failure", 0)
rule("code", "medium", "code-test-skip",
     r"@pytest\.mark\.skip\b|\bpytest\.skip\(|\b(?:it|describe|test)\.skip\(|\bxit\(|\bxdescribe\(|@Disabled\b"
     r"|\bt\.Skip\(|#\[ignore\]|@unittest\.skip|--passWithNoTests|\|\|\s*true\b",
     "skipped or bypassed test; restore it unless it links to an issue", 0)
rule("code", "medium", "code-version-name",
     r"\b(?:def|function|class|const|let|var|fn|func|type|interface)\s+(?:\w*(?:_fixed|_enhanced|_improved|_backup)"
     r"|(?:Enhanced|Improved|Fixed)[A-Z]\w*|\w+(?:Enhanced|Improved|Fixed))\b",
     "version-ish name; use the plain name and replace the old one", 0)
rule("code", "weak", "code-weak-assertion", r"\bassert True\b|expect\(true\)|\.toBeDefined\(\)|\.toBeTruthy\(\)",
     "weak assertion; assert the actual expected value", 0)
rule("code", "weak", "code-banner", r"\bprint\(\s*[\"'][=\-*#]{10,}|\bprint\(\s*[\"'][=\-*#][\"']\s*\*\s*\d+",
     "banner print; remove it or use the project's logger", 0)

ORDERED = sorted(RULES, key=lambda item: -LEVELS[item[1]])


def is_prose(path):
    return path is None or Path(path).suffix.lower() in PROSE_SUFFIXES


def scan_texts(texts):
    hits = []
    taken = {}
    for scope, level, rule_id, pattern, hint in ORDERED:
        text = texts.get(scope)
        if text is None:
            continue
        spans = taken.setdefault(scope if scope in ("raw", "pair", "code") else "clean", [])
        for match in pattern.finditer(text):
            start, end = match.span()
            if any(start < other_end and other_start < end for other_start, other_end in spans):
                continue
            spans.append((start, end))
            hits.append({"level": level, "rule": rule_id, "match": match.group(0).strip(), "hint": hint})
    return hits


def scan_lines(path, numbered_lines):
    prose = is_prose(path)
    fenced = False
    front_matter = False
    previous = None
    findings = []
    stats = {"words": 0, "em_dashes": 0, "ko_clauses": 0, "ko_clause_commas": 0}
    for index, (number, text, wanted) in enumerate(numbered_lines):
        if prose and index == 0 and number == 1 and text.strip() == "---":
            front_matter = True
            continue
        if front_matter:
            front_matter = text.strip() != "---"
            continue
        if prose and FENCE.match(text):
            fenced = not fenced
            continue
        texts = {}
        if prose:
            if fenced or text.lstrip().startswith(">"):
                continue
            raw = INLINE_CODE.sub(" ", text)
            clean = URL.sub(" ", raw)
            texts.update(raw=raw, prose=clean, markup=clean)
        else:
            comment = COMMENT.match(text) or TRAILING_COMMENT.search(text)
            texts.update(raw=text, code=text)
            if comment:
                clean = URL.sub(" ", comment.group(1))
                texts.update(prose=clean, comment=clean)
            if previous is not None:
                texts["pair"] = previous + "\n" + text
            previous = text
        if not wanted:
            continue
        if "prose" in texts:
            clean = texts["prose"]
            stats["words"] += len(WORD.findall(clean))
            stats["em_dashes"] += clean.count("—")
            for match in KO_CLAUSE.finditer(clean):
                stats["ko_clauses"] += 1
                stats["ko_clause_commas"] += bool(match.group(1))
        for hit in scan_texts(texts):
            hit.update(path=path or "-", line=number)
            findings.append(hit)
    return findings, stats


def parse_diff(text):
    files = {}
    path = None
    number = 0
    for line in text.splitlines():
        if line.startswith("+++ "):
            target = line[4:].split("\t")[0].strip()
            path = None if target == "/dev/null" else re.sub(r"^b/", "", target)
            if path is not None:
                files.setdefault(path, [])
        elif line.startswith("@@"):
            start = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", line)
            number = int(start.group(1)) if start else 0
        elif path is None or line.startswith(("--- ", "diff ", "index ", "\\")):
            continue
        elif line.startswith("+"):
            files[path].append((number, line[1:], True))
            number += 1
        elif line.startswith(" "):
            files[path].append((number, line[1:], False))
            number += 1
    return files


def scan_inputs(args):
    sources = []
    if args.diff:
        diff = sys.stdin.read() if args.diff == "-" else Path(args.diff).read_text(encoding="utf-8")
        sources += parse_diff(diff).items()
    for target in args.paths or ([] if args.diff else ["-"]):
        if target == "-":
            text, path = sys.stdin.read(), args.stdin_name
        else:
            text, path = Path(target).read_text(encoding="utf-8"), target
        sources.append((path, [(n, line, True) for n, line in enumerate(text.splitlines(), 1)]))
    findings = []
    totals = {"words": 0, "em_dashes": 0, "ko_clauses": 0, "ko_clause_commas": 0}
    for path, lines in sources:
        found, stats = scan_lines(path, lines)
        findings += found
        for key in totals:
            totals[key] += stats[key]
    return findings, totals


def summarize(findings, totals):
    words = totals["words"]
    clauses = totals["ko_clauses"]
    return {
        "prose_words": words,
        "counts": {level: sum(1 for hit in findings if hit["level"] == level) for level in LEVELS},
        "hits_per_1000_words": round(len(findings) * 1000 / words, 1) if words else None,
        "em_dashes_per_1000_words": round(totals["em_dashes"] * 1000 / words, 1) if words else None,
        "ko_clause_comma_ratio": round(totals["ko_clause_commas"] / clauses, 2) if clauses >= 5 else None,
    }


def main():
    parser = argparse.ArgumentParser(description="Flag candidate AI-slop patterns in prose, docs, and code. "
                                                 "Hits are leads for review, not verdicts.")
    parser.add_argument("paths", nargs="*", help="files to scan; '-' or nothing reads stdin")
    parser.add_argument("--diff", metavar="FILE", help="scan only added lines of a unified diff ('-' for stdin)")
    parser.add_argument("--stdin-name", help="file name that decides prose or code rules for stdin input")
    parser.add_argument("--min", choices=LEVELS, default="weak", help="lowest level to report")
    parser.add_argument("--fail-on", choices=LEVELS, help="exit 1 when a hit at or above this level remains")
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    args = parser.parse_args()
    try:
        findings, totals = scan_inputs(args)
    except (OSError, UnicodeDecodeError) as error:
        print(f"scan.py: {error}", file=sys.stderr)
        return 2
    findings = [hit for hit in findings if LEVELS[hit["level"]] >= LEVELS[args.min]]
    summary = summarize(findings, totals)
    if args.json:
        json.dump({"summary": summary, "findings": findings}, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        for hit in findings:
            print(f"{hit['path']}:{hit['line']}: {hit['level']} {hit['rule']}: {hit['match']!r} | {hit['hint']}")
        counts = summary["counts"]
        line = (f"{len(findings)} hits (strong {counts['strong']}, medium {counts['medium']}, weak {counts['weak']}),"
                f" {summary['prose_words']} prose words")
        if summary["hits_per_1000_words"] is not None:
            line += (f", {summary['hits_per_1000_words']} hits and {summary['em_dashes_per_1000_words']}"
                     " em dashes per 1000 words")
        if summary["ko_clause_comma_ratio"] is not None:
            line += f", Korean clause-ending comma ratio {summary['ko_clause_comma_ratio']}"
        print(line)
    threshold = LEVELS[args.fail_on] if args.fail_on else None
    return int(threshold is not None and any(LEVELS[hit["level"]] >= threshold for hit in findings))


if __name__ == "__main__":
    raise SystemExit(main())
