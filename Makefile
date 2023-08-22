SOURCE_URL := "https://www.youtube.com/@gracechristiancommunity5971"

run:
	# Download audio
	@youtube-dl \
		-x \
		-o 'assets/audio/%(id)s.%(ext)s' \
		--audio-format mp3 \
		--download-archive downloaded.txt \
		--no-post-overwrites \
		--print-json \
		$(SOURCE_URL) \
		| jq '{"id": .id, "title": .title | gsub("\""; "\\\""), "date": .upload_date, "duration": .duration}' \
		| jq -r '\
			to_entries \
			| map("  \(.key): \"\(.value | tostring)\"") \
			| join("\n") \
		' \
		| sed -E \
			-e 's/  id: /- id: /g' \
			-e 's/date: "([0-9]{4})([0-9]{2})([0-9]{2})"/date: "\1-\2-\3 00:00:00+00:00"/g' \
		>> _data/episodes.yml

	# Remove EXIF data from audio files
	@exiftool \
		-overwrite_original \
		assets/audio/

	# Build with Jekyll
	@bundle exec jekyll build
