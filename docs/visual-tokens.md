# Usage

All you have to do is running this command:

```bash
bin/generate_visual_token.sh
```

As we use Javascript to render the visual tokens, this task take a lot of time to finish. Therefore it's not ideal to run this in Ansible. We created it as a shell script so that we can take advantage of a window managing tool such as [screen](https://www.gnu.org/software/screen/manual/screen.html)

# Explanation

There are 3 things the command above does:

- Generate the visual_token and save them in visual_token_media_path (which you can find in ansible/roles/web/defaults/main.yml)
- Optimize the images created to make them shrink in size.
- Upload them to Azure storage

# Urls

After the process finishes, you can find the images at:

- PNG: https://[azure-account].blob.core.windows.net/visual-token/officer_[id]_[social-platform]_share.png
- SVG: https://[azure-account].blob.core.windows.net/visual-token/officer_[id].svg

With:

- azure-account: cpdbdev, cpdbvisualtokenstaging, cpdbvisualtoken for development, staging and production
- id: the id of the officer that you want to get the visual token
- social-platform: facebook or twitter

The background color for each token is included in the officer object.

# How to add a new renderer

- Create a js renderer file that defines `window.render`, this must call `clearDrawingArea` function.

- Add a new renderer class in renderers.py which includes:
  + the script_path to the js renderer
  + `serialize` function that takes in a django object and returns the json data
  + `blob_name` function that returns the name of the Azure blob that you want your tokens to upload to

- Use `open_engine` to open your newly created renderer in cpdb/visual_token/managerment/commands/generate_visual_token.py

```python
with open_engine(renderer) as engine:
    ...
```
