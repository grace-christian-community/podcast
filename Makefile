SOURCE_URL := "https://www.youtube.com/@gracechristiancommunity5971"

update: clean
	@mkdir temp
	$(MAKE) download-audio
	$(MAKE) download-metadata
	$(MAKE) clean

serve:
	@bundle exec jekyll serve

clean:
	-@rm -rf temp
	-@rm -rf _site
	-@rm assets/audio/*.part

download-audio:
	# Create download archive
	@ls assets/audio/ \
		| sed s/\.mp3//g \
		| sed 's/^/youtube /g' \
		> temp/download_archive.txt

	# Download audio files
	@youtube-dl \
		-x \
		-o 'assets/audio/%(id)s.%(ext)s' \
		--audio-format mp3 \
		--download-archive temp/download_archive.txt \
		--no-post-overwrites \
		$(SOURCE_URL)

	# Remove EXIF data from audio files
	@exiftool \
		-overwrite_original \
		assets/audio/

download-metadata:
	# Write to episodes.yml
	@ls assets/audio/ \
		| sed s/\.mp3//g \
		| sed 's/^/https:\/\/www.youtube.com\/watch?v=/g' \
		> temp/downloaded_video_links.txt
	@youtube-dl \
		--skip-download \
		--print-json \
		-a temp/downloaded_video_links.txt \
		| jq ' \
			{ \
				"id": .id, \
				"title": .title | gsub("\""; "\\\""), \
				"date": .upload_date, \
				"duration": .duration \
			} \
		' \
		| jq -r ' \
			to_entries \
			| map("  \(.key): \"\(.value | tostring)\"") \
			| join("\n") \
		' \
		| sed -E \
			-e 's/  id: /- id: /g' \
			-e 's/date: "([0-9]{4})([0-9]{2})([0-9]{2})"/date: "\1-\2-\3 00:00:00+00:00"/g' \
		> _data/episodes.yml
