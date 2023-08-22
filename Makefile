SOURCE_URL := "https://www.youtube.com/@gracechristiancommunity5971"

run:
	# Download audio
	@youtube-dl \
		-x \
		-o 'assets/audio/%(id)s.%(ext)s' \
		--audio-format mp3 \
		--download-archive downloaded.txt \
		--no-post-overwrites \
		$(SOURCE_URL)
	
	# Write to episodes.yml
	@ls assets/audio/ | sed s/\.mp3//g | sed 's/^/https:\/\/www.youtube.com\/watch?v=/g' > downloaded_video_links.txt.temp
	@youtube-dl \
		--skip-download \
		--print-json \
		-a downloaded_video_links.txt.temp \
		| jq '{"id": .id, "title": .title | gsub("\""; "\\\""), "date": .upload_date, "duration": .duration}' \
		| jq -r '\
			to_entries \
			| map("  \(.key): \"\(.value | tostring)\"") \
			| join("\n") \
		' \
		| sed -E \
			-e 's/  id: /- id: /g' \
			-e 's/date: "([0-9]{4})([0-9]{2})([0-9]{2})"/date: "\1-\2-\3 00:00:00+00:00"/g' \
		> _data/episodes.yml
	-@rm downloaded_video_links.txt.temp

	# Remove EXIF data from audio files
	@exiftool \
		-overwrite_original \
		assets/audio/

	# Build with Jekyll
	@bundle exec jekyll build
