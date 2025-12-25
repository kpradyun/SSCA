#!/bin/bash

OUTPUT_FILE="combined.dot"

echo "digraph G {" > "$OUTPUT_FILE"

for file in *.dot; do
    [[ "$file" == "$OUTPUT_FILE" ]] && continue

    echo "Processing file: $file"

    echo "// From $file" >> "$OUTPUT_FILE"

    awk '
        BEGIN {depth=0; inside=0}
        {
            # Increase depth on '{', decrease on '}'
            for(i=1; i<=length($0); i++) {
                c = substr($0, i, 1)
                if(c == "{") depth++
                if(c == "}") depth--
            }
            # Start printing when inside first brace
            if(depth > 0) inside=1
            if(inside && depth > 0) {
                if($0 !~ /^[ \t]*\{[ \t]*$/ && $0 !~ /^[ \t]*\}[ \t]*$/) print
            }
        }
    ' "$file" >> "$OUTPUT_FILE"

    echo >> "$OUTPUT_FILE"
done

echo "}" >> "$OUTPUT_FILE"

echo "Combined DOT file created as $OUTPUT_FILE"

