# -*- coding: utf-8 -*-
import urllib2
import json
import logging

from collections import namedtuple
from mercurial.cmdutil import show_changeset

config_group = 'slackhooks'
Config = namedtuple(
    'HgSlackHooksConfig',
    field_names=[
        'org_name',
        'webhook_url',
        'repo_name',
        'commit_url',
        'username',
        'icon_emoji',
        'icon_url',
    ])

def get_config(ui):
    org_name = ui.config(config_group, 'org_name')
    webhook_url = ui.config(config_group, 'webhook_url')
    repo_name = ui.config(config_group, 'repo_name', default=None)
    commit_url = ui.config(config_group, 'commit_url', default=None)
    username = ui.config(config_group, 'username', default="mercurial")
    icon_emoji = ui.config(config_group, 'icon_emoji', default=None)
    icon_url = ui.config(config_group, 'icon_url', default=None)

    return Config(org_name, webhook_url, repo_name, commit_url, username, icon_emoji,
                  icon_url)


def pushhook(ui, repo, node, source, **kwargs):
    if source != 'push':
        return
    config = get_config(ui)
    branch = repo[kwargs.get('parent1')].branch()
    changesets = get_changesets(repo, node, branch)
    count = len(changesets)
    messages = render_changesets(ui, repo, changesets, config)

    ensure_plural = "s" if count > 1 else ""
    ensure_branch_name = " to branch *{0}*".format(branch) if branch else ""
    ensure_repo_name = " in _{0}_".format(config.repo_name) if config.repo_name else ""

    text = "Pushed {count} changeset{ensure_plural}{ensure_branch_name}{ensure_repo_name}:\n```{changes}```".format(
        count=count,
        ensure_plural=ensure_plural,
        ensure_branch_name=ensure_branch_name,
        ensure_repo_name=ensure_repo_name,
        changes=messages)

    post_message_to_slack(text, config)


def get_changesets(repo, node, branch):
    node_rev = repo[node].rev()
    tip_rev = repo['tip'].rev()
    changesets = []
    for rev in range(tip_rev, node_rev - 1, -1):
        if repo[rev].branch() == branch:
            changesets.append(rev)
    return changesets


def render_changesets(ui, repo, changesets, config):
    url = config.commit_url
    if url:
        node_template = "<{url}{{node|short}}|{{node|short}}>".format(url=url)
    else:
        node_template = "{node|short}"

    template = "{0}\\n".format(" | ".join([
        "{branch}",
        node_template,
        "{date(date, '%Y-%m-%d [%H:%M:%S]')}",
        "{desc|strip|firstline}",
    ]))

    displayer = show_changeset(ui, repo, {'template': template})
    ui.pushbuffer()
    for rev in changesets:
        displayer.show(repo[rev])
    return ui.popbuffer()


def post_message_to_slack(message, config):
    target_url = "{webhook_url}".format(webhook_url=config.webhook_url)
    payload = {
        'text': message,
        'username': config.username,
    }
    payload_optional_key(payload, config, 'icon_url')
    payload_optional_key(payload, config, 'icon_emoji')
    request = urllib2.Request(target_url, "payload={0}".format(json.dumps(payload)))
    urllib2.build_opener().open(request)

def print_keyword_args(**kwargs):
    # kwargs is a dict of the keyword args passed to the function
    for key, value in kwargs.iteritems():
        print "%s = %s" % (key, value)

def on_update(ui, repo, **kwargs):
    #print_keyword_args(**kwargs)
    config = get_config(ui)
    branch = repo[kwargs.get('parent1')].branch()
    text = "Updated to branch `{branch}`".format(
        branch=branch
    )

    post_message_to_slack(text, config)

def payload_optional_key(payload, config, key):
    value = config.__getattribute__(key)
    if value:
        payload[key] = value
