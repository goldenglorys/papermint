def dump_latex_template(temp_dir):
    template = r"""\PassOptionsToPackage{unicode$for(hyperrefoptions)$,$hyperrefoptions$$endfor$}{hyperref}
\PassOptionsToPackage{hyphens}{url}
$if(colorlinks)$
\PassOptionsToPackage{dvipsnames,svgnames,x11names}{xcolor}
$endif$
$if(dir)$
$if(latex-dir-rtl)$
\PassOptionsToPackage{RTLdocument}{bidi}
$endif$
$endif$
$if(CJKmainfont)$
\PassOptionsToPackage{space}{xeCJK}
$endif$
%
\documentclass[
$if(fontsize)$
  $fontsize$,
$endif$
$if(lang)$
  $babel-lang$,
$endif$
$if(papersize)$
  $papersize$paper,
$endif$
$for(classoption)$
  $classoption$$sep$,
$endfor$
]{$documentclass$}
\usepackage{cite}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{algorithmic}
$if(fontfamily)$
\usepackage[$for(fontfamilyoptions)$$fontfamilyoptions$$sep$,$endfor$]{$fontfamily$}
$else$
\usepackage{lmodern}
$endif$
$if(linestretch)$
\usepackage{setspace}
$endif$
\usepackage{iftex}
\ifPDFTeX
  \usepackage[$if(fontenc)$$fontenc$$else$T1$endif$]{fontenc}
  \usepackage[utf8]{inputenc}
  \usepackage{textcomp} % provide euro and other symbols
\else % if luatex or xetex
$if(mathspec)$
  \ifXeTeX
    \usepackage{mathspec}
  \else
    \usepackage{unicode-math}
  \fi
$else$
  \usepackage{unicode-math}
$endif$
  \defaultfontfeatures{Scale=MatchLowercase}
  \defaultfontfeatures[\rmfamily]{Ligatures=TeX,Scale=1}
$if(mainfont)$
  \setmainfont[$for(mainfontoptions)$$mainfontoptions$$sep$,$endfor$]{$mainfont$}
$endif$
$if(sansfont)$
  \setsansfont[$for(sansfontoptions)$$sansfontoptions$$sep$,$endfor$]{$sansfont$}
$endif$
$if(monofont)$
  \setmonofont[$for(monofontoptions)$$monofontoptions$$sep$,$endfor$]{$monofont$}
$endif$
$for(fontfamilies)$
  \newfontfamily{$fontfamilies.name$}[$for(fontfamilies.options)$$fontfamilies.options$$sep$,$endfor$]{$fontfamilies.font$}
$endfor$
$if(mathfont)$
$if(mathspec)$
  \ifXeTeX
    \setmathfont(Digits,Latin,Greek)[$for(mathfontoptions)$$mathfontoptions$$sep$,$endfor$]{$mathfont$}
  \else
    \setmathfont[$for(mathfontoptions)$$mathfontoptions$$sep$,$endfor$]{$mathfont$}
  \fi
$else$
  \setmathfont[$for(mathfontoptions)$$mathfontoptions$$sep$,$endfor$]{$mathfont$}
$endif$
$endif$
$if(CJKmainfont)$
  \ifXeTeX
    \usepackage{xeCJK}
    \setCJKmainfont[$for(CJKoptions)$$CJKoptions$$sep$,$endfor$]{$CJKmainfont$}
  \fi
$endif$
$if(luatexjapresetoptions)$
  \ifLuaTeX
    \usepackage[$for(luatexjapresetoptions)$$luatexjapresetoptions$$sep$,$endfor$]{luatexja-preset}
  \fi
$endif$
$if(CJKmainfont)$
  \ifLuaTeX
    \usepackage[$for(luatexjafontspecoptions)$$luatexjafontspecoptions$$sep$,$endfor$]{luatexja-fontspec}
    \setmainjfont[$for(CJKoptions)$$CJKoptions$$sep$,$endfor$]{$CJKmainfont$}
  \fi
$endif$
\fi
$if(zero-width-non-joiner)$
%% Support for zero-width non-joiner characters.
\makeatletter
\def\zerowidthnonjoiner{%
  % Prevent ligatures and adjust kerning, but still support hyphenating.
  \texorpdfstring{%
    \textormath{\nobreak\discretionary{-}{}{\kern.03em}%
      \ifvmode\else\nobreak\hskip\z@skip\fi}{}%
  }{}%
}
\makeatother
\ifPDFTeX
  \DeclareUnicodeCharacter{200C}{\zerowidthnonjoiner}
\else
  \catcode`^^^^200c=\active
  \protected\def ^^^^200c{\zerowidthnonjoiner}
\fi
%% End of ZWNJ support
$endif$
% Use upquote if available, for straight quotes in verbatim environments
\IfFileExists{upquote.sty}{\usepackage{upquote}}{}
\IfFileExists{microtype.sty}{% use microtype if available
  \usepackage[$for(microtypeoptions)$$microtypeoptions$$sep$,$endfor$]{microtype}
  \UseMicrotypeSet[protrusion]{basicmath} % disable protrusion for tt fonts
}{}
$if(indent)$
$else$
\makeatletter
\@ifundefined{KOMAClassName}{% if non-KOMA class
  \IfFileExists{parskip.sty}{%
    \usepackage{parskip}
  }{% else
    \setlength{\parindent}{0pt}
    \setlength{\parskip}{6pt plus 2pt minus 1pt}}
}{% if KOMA class
  \KOMAoptions{parskip=half}}
\makeatother
$endif$
$if(verbatim-in-note)$
\usepackage{fancyvrb}
$endif$
\usepackage{xcolor}
\IfFileExists{xurl.sty}{\usepackage{xurl}}{} % add URL line breaks if available
\IfFileExists{bookmark.sty}{\usepackage{bookmark}}{\usepackage{hyperref}}
\hypersetup{
$if(title-meta)$
  pdftitle={$title-meta$},
$endif$
$if(author-meta)$
  pdfauthor={$author-meta$},
$endif$
$if(lang)$
  pdflang={$lang$},
$endif$
$if(subject)$
  pdfsubject={$subject$},
$endif$
$if(keywords)$
  pdfkeywords={$for(keywords)$$keywords$$sep$, $endfor$},
$endif$
$if(colorlinks)$
  colorlinks=true,
  linkcolor={$if(linkcolor)$$linkcolor$$else$Maroon$endif$},
  filecolor={$if(filecolor)$$filecolor$$else$Maroon$endif$},
  citecolor={$if(citecolor)$$citecolor$$else$Blue$endif$},
  urlcolor={$if(urlcolor)$$urlcolor$$else$Blue$endif$},
$else$
  hidelinks,
$endif$
  pdfcreator={LaTeX via pandoc}}
\urlstyle{same} % disable monospaced font for URLs
$if(verbatim-in-note)$
\VerbatimFootnotes % allow verbatim text in footnotes
$endif$
$if(geometry)$
\usepackage[$for(geometry)$$geometry$$sep$,$endfor$]{geometry}
$endif$
$if(listings)$
\usepackage{listings}
\newcommand{\passthrough}[1]{#1}
\lstset{defaultdialect=[5.3]Lua}
\lstset{defaultdialect=[x86masm]Assembler}
$endif$
$if(lhs)$
\lstnewenvironment{code}{\lstset{language=Haskell,basicstyle=\small\ttfamily}}{}
$endif$
$if(highlighting-macros)$
$highlighting-macros$
$endif$
$if(tables)$
\usepackage{longtable,booktabs,array}

% https://tex.stackexchange.com/a/224096
\makeatletter
\let\oldlt\longtable
\let\endoldlt\endlongtable
\def\longtable{\@ifnextchar[\longtable@i \longtable@ii}
\def\longtable@i[#1]{\begin{figure}[t]
\onecolumn
\begin{minipage}{0.5\textwidth}
\oldlt[#1]
}
\def\longtable@ii{\begin{figure}[t]
\onecolumn
\begin{minipage}{0.5\textwidth}
\oldlt
}
\def\endlongtable{\endoldlt
\end{minipage}
\twocolumn
\end{figure}}
\makeatother


$if(multirow)$
\usepackage{multirow}
$endif$
\usepackage{calc} % for calculating minipage widths
% Correct order of tables after \paragraph or \subparagraph
\usepackage{etoolbox}
\makeatletter
\patchcmd\longtable{\par}{\if@noskipsec\mbox{}\fi\par}{}{}
\makeatother
% Allow footnotes in longtable head/foot
\IfFileExists{footnotehyper.sty}{\usepackage{footnotehyper}}{\usepackage{footnote}}
\makesavenoteenv{longtable}
$endif$
$if(graphics)$
\usepackage{graphicx}
\makeatletter
\def\maxwidth{\ifdim\Gin@nat@width>\linewidth\linewidth\else\Gin@nat@width\fi}
\def\maxheight{\ifdim\Gin@nat@height>\textheight\textheight\else\Gin@nat@height\fi}
\makeatother
% Scale images if necessary, so that they will not overflow the page
% margins by default, and it is still possible to overwrite the defaults
% using explicit options in \includegraphics[width, height, ...]{}
\setkeys{Gin}{width=\maxwidth,height=\maxheight,keepaspectratio}
% Set default figure placement to htbp
\makeatletter
\def\fps@figure{htbp}
\makeatother
$endif$
$if(links-as-notes)$
% Make links footnotes instead of hotlinks:
\DeclareRobustCommand{\href}[2]{#2\footnote{\url{#1}}}
$endif$
$if(strikeout)$
$-- also used for underline
\usepackage[normalem]{ulem}
% Avoid problems with \sout in headers with hyperref
\pdfstringdefDisableCommands{\renewcommand{\sout}{}}
$endif$
\setlength{\emergencystretch}{3em} % prevent overfull lines
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
$if(numbersections)$
\setcounter{secnumdepth}{$if(secnumdepth)$$secnumdepth$$else$5$endif$}
$else$
\setcounter{secnumdepth}{-\maxdimen} % remove section numbering
$endif$
$if(block-headings)$
% Make \paragraph and \subparagraph free-standing
\ifx\paragraph\undefined\else
  \let\oldparagraph\paragraph
  \renewcommand{\paragraph}[1]{\oldparagraph{#1}\mbox{}}
\fi
\ifx\subparagraph\undefined\else
  \let\oldsubparagraph\subparagraph
  \renewcommand{\subparagraph}[1]{\oldsubparagraph{#1}\mbox{}}
\fi
$endif$
$if(pagestyle)$
\pagestyle{$pagestyle$}
$endif$
$if(csl-refs)$
\newlength{\cslhangindent}
\setlength{\cslhangindent}{1.5em}
\newlength{\csllabelwidth}
\setlength{\csllabelwidth}{3em}
\newlength{\cslentryspacingunit} % times entry-spacing
\setlength{\cslentryspacingunit}{\parskip}
\newenvironment{CSLReferences}[2] % #1 hanging-ident, #2 entry spacing
 {% dont indent paragraphs
  \setlength{\parindent}{0pt}
  % turn on hanging indent if param 1 is 1
  \ifodd #1
  \let\oldpar\par
  \def\par{\hangindent=\cslhangindent\oldpar}
  \fi
  % set entry spacing
  \setlength{\parskip}{#2\cslentryspacingunit}
 }%
 {}
\usepackage{calc}
\newcommand{\CSLBlock}[1]{#1\hfill\break}
\newcommand{\CSLLeftMargin}[1]{\parbox[t]{\csllabelwidth}{#1}}
\newcommand{\CSLRightInline}[1]{\parbox[t]{\linewidth - \csllabelwidth}{#1}\break}
\newcommand{\CSLIndent}[1]{\hspace{\cslhangindent}#1}
$endif$
$for(header-includes)$
$header-includes$
$endfor$
$if(lang)$
\ifXeTeX
  % Load polyglossia as late as possible: uses bidi with RTL langages (e.g. Hebrew, Arabic)
  \usepackage{polyglossia}
  \setmainlanguage[$for(polyglossia-lang.options)$$polyglossia-lang.options$$sep$,$endfor$]{$polyglossia-lang.name$}
$for(polyglossia-otherlangs)$
  \setotherlanguage[$for(polyglossia-otherlangs.options)$$polyglossia-otherlangs.options$$sep$,$endfor$]{$polyglossia-otherlangs.name$}
$endfor$
\else
  \usepackage[$for(babel-otherlangs)$$babel-otherlangs$,$endfor$main=$babel-lang$]{babel}
% get rid of language-specific shorthands (see #6817):
\let\LanguageShortHands\languageshorthands
\def\languageshorthands#1{}
$if(babel-newcommands)$
  $babel-newcommands$
$endif$
\fi
$endif$
\ifLuaTeX
  \usepackage{selnolig}  % disable illegal ligatures
\fi
$if(dir)$
\ifXeTeX
  % Load bidi as late as possible as it modifies e.g. graphicx
  \usepackage{bidi}
\fi
\ifPDFTeX
  \TeXXeTstate=1
  \newcommand{\RL}[1]{\beginR #1\endR}
  \newcommand{\LR}[1]{\beginL #1\endL}
  \newenvironment{RTL}{\beginR}{\endR}
  \newenvironment{LTR}{\beginL}{\endL}
\fi
$endif$
$if(natbib)$
\usepackage[$natbiboptions$]{natbib}
\bibliographystyle{$if(biblio-style)$$biblio-style$$else$plainnat$endif$}
$endif$
$if(biblatex)$
\usepackage[$if(biblio-style)$style=$biblio-style$,$endif$$for(biblatexoptions)$$biblatexoptions$$sep$,$endfor$]{biblatex}
$for(bibliography)$
\addbibresource{$bibliography$}
$endfor$
$endif$
$if(nocite-ids)$
\nocite{$for(nocite-ids)$$it$$sep$, $endfor$}
$endif$
\usepackage{csquotes}

$if(title)$
\title{$title$$if(thanks)$\thanks{$thanks$}$endif$}
$endif$

\markboth{$if(journal)$$journal$$endif$}{$if(title)$$title$$endif$}

$if(subtitle)$
\usepackage{etoolbox}
\makeatletter
\providecommand{\subtitle}[1]{% add subtitle to \maketitle
  \apptocmd{\@title}{\par {\large #1 \par}}{}{}
}
\makeatother
\subtitle{$subtitle$}
$endif$
\author{$for(author)$$author$$sep$ \and $endfor$}
\date{$date$}

\begin{document}
$if(has-frontmatter)$
\frontmatter
$endif$
$if(title)$
\maketitle
$if(abstract)$
\begin{abstract}
$abstract$
\end{abstract}
$endif$
$endif$

$for(include-before)$
$include-before$

$endfor$
$if(toc)$
$if(toc-title)$
\renewcommand*\contentsname{$toc-title$}
$endif$
{
$if(colorlinks)$
\hypersetup{linkcolor=$if(toccolor)$$toccolor$$else$$endif$}
$endif$
\setcounter{tocdepth}{$toc-depth$}
\tableofcontents
}
$endif$
$if(lof)$
\listoffigures
$endif$
$if(lot)$
\listoftables
$endif$
$if(linestretch)$
\setstretch{$linestretch$}
$endif$
$if(has-frontmatter)$
\mainmatter
$endif$
$body$

$if(has-frontmatter)$
\backmatter
$endif$
$if(natbib)$
$if(bibliography)$
$if(biblio-title)$
$if(has-chapters)$
\renewcommand\bibname{$biblio-title$}
$else$
\renewcommand\refname{$biblio-title$}
$endif$
$endif$
  \bibliography{$for(bibliography)$$bibliography$$sep$,$endfor$}

$endif$
$endif$
$if(biblatex)$
\printbibliography$if(biblio-title)$[title=$biblio-title$]$endif$

$endif$
$for(include-after)$
$include-after$

$endfor$
\end{document}"""
    with open(f"{temp_dir}/template.tex", "w") as f:
        f.write(template)
