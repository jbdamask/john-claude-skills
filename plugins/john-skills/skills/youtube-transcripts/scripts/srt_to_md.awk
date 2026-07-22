# Convert a YouTube auto-caption .srt into readable markdown with timestamps.
#
# Expects the .srt to have come from YouTube's ttml caption format (see
# --sub-format in fetch_transcripts.sh), where each spoken phrase appears
# exactly once. The ttml -> srt conversion wraps every line in styling tags
# like <font color="white">, which are stripped here.
#
# Variables:
#   chunk   0 = one line per caption line (default)
#           N = group text into ~N-second paragraphs
#   stamps  1 = prefix each line/paragraph with [HH:MM:SS] (default)
#           0 = omit the timestamps, leaving plain prose

function hms(t,   h, m, s) {
  h = int(t / 3600); m = int((t % 3600) / 60); s = int(t % 60)
  return sprintf("%02d:%02d:%02d", h, m, s)
}

# Timestamp prefix, or nothing when stamps=0.
function stamp(t) {
  return stamps ? "[" hms(t) "] " : ""
}

BEGIN { if (stamps == "") stamps = 1 }

function tosec(str,   p) {
  split(str, p, ":")
  sub(",", ".", p[3])
  return p[1] * 3600 + p[2] * 60 + p[3]
}

/-->/                  { ts = tosec($1); next }
/^[0-9]+$/             { next }   # cue index lines
/^[[:space:]]*$/       { next }

{
  line = $0
  gsub(/<[^>]*>/, "", line)
  gsub(/^[[:space:]]+|[[:space:]]+$/, "", line)
  if (line == "") next

  if (chunk == 0) {
    print stamp(ts) line
    next
  }

  if (buf == "") start = ts
  buf = (buf == "" ? line : buf " " line)
  if (ts - start >= chunk) {
    print stamp(start) buf
    print ""
    buf = ""
  }
}

END {
  if (chunk > 0 && buf != "") print stamp(start) buf
}
