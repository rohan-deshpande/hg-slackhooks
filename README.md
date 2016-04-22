# hg-slackhooks

Mercurial server-side hooks for Slack messaging service.

## Examples

To add push hooks for some repo, modify ``.hg/hgrc`` in the central repository:

```
    [slackhooks]
    org_name = YOUR_ORGANIZATION_NAME
    webhook_url = YOUR_WEBHOOK_URL
    repo_name = YOUR_REPO_NAME
    username = YOUR_USER_NAME
    commit_url = http://example.com/101-sandbox/rev/
    icon_emoji = :turtle:

    [hooks]
    changegroup.slackhooks= python:/path/to/slackhooks.py:pushhook
```

Example of chat message output:

![example](http://i.imgur.com/Ivcctgq.png)

## Options

* `org_name` is the name of your organization. *It's obligatory and it's a part of your unique webhook URL.*
* `webhook_url` is your webhook URL endpoint, check `https://<your-team>.slack.com/services/` to find yours.
* `repo_name` is a name of your repository. *It's optional.*
* `commit_url` is a part of URL for parcilular changeset. If it is specified, link to a changeset will be inserted in description of changeset. Plain text short revision number will be used otherwise.
* `username` is the displayed name. Default: `mercurial`.
* `icon_emoji` is the name of emoticon, which will be displayed. *It's optional.* You can use ``icon_url`` instead.
* `icon_url` is a direct link to image, which will be displayed. *It's optional.* You can use
   this icon URL `<https://raw.githubusercontent.com/oblalex/hg-slackhooks/master/assets/mercurial.png>` if you want.
* `icon_emoji` and `icon_url` are both optional and interchangeable.

## Testing

You can test any hg hook and command by running the following code in your terminal while inside the repo

`hg --config hooks.pre-commit="export| grep HG_" commit`

Where `pre-commit` can be any hook you want to test and `commit` can be any command you want to test.
