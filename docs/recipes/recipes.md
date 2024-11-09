---
description: Syntask Recipes provide extensible examples for common Syntask use cases.
tags:
    - recipes
    - best practices
    - examples
hide:
  - toc
search:
  boost: 2
---

# Syntask Recipes

[Syntask recipes](https://github.com/Synopkg/syntask-recipes) are common, extensible examples for setting up Syntask in your execution environment with ready-made ingredients such as Dockerfiles, Terraform files, and GitHub Actions.

Recipes are useful when you are looking for tutorials on how to deploy a worker, use event-driven flows, set up unit testing, and more.

The following are Syntask recipes specific to Syntask 2. You can find a full repository of recipes at [https://github.com/Synopkg/syntask-recipes](https://github.com/Synopkg/syntask-recipes) and additional recipes at [Syntask Discourse](https://discourse.syntask.io/).

## Recipe catalog

<!-- The code below is a jinja2 template that will be rendered by generate_catalog.py -->
<div class="recipe-grid">
{% for collection in collections %}
    <div class="recipe-item">
        <div class="recipe-title">
            <a href="{{ collection['recipeUrl'] }}">
                <h3 style="margin: 0">{{collection['recipeName']}}</h3>
            </a>
        </div>
        <div class="recipe-desc">
            <p>
                {{ collection["description"] }}
            </p>
        </div>
        <div class="recipe-details">
            <p>
                Maintained by <a href="{{ collection["authorUrl"] }}">{{ collection["author"] }}</a>
            </p>
            <p>
                This recipe uses:
            </p>
            <p>
                {% for icon in collection['iconUrl'] %}
                    <img src="{{ icon }}" >
                {% endfor %}
            </p>
        </div>
    </div>
{% endfor %}
</div >

## Contributing recipes

We're always looking for new recipe contributions! See the [Syntask Recipes](https://github.com/Synopkg/syntask-recipes#contributing--swag-) repository for details on how you can add your Syntask recipe, share best practices with fellow Syntask users, and earn some swag.

[Syntask recipes](https://github.com/Synopkg/syntask-recipes) provide a vital cookbook where users can find helpful code examples and, when appropriate, common steps for specific Syntask use cases.

We love recipes from anyone who has example code that another Syntask user can benefit from (e.g. a Syntask flow that loads data into Snowflake).

Have a blog post, Discourse article, or tutorial you’d like to share as a recipe? All submissions are welcome. Clone the syntask-recipes repo, create a branch, add a link to your recipe to the README, and submit a PR. Have more questions? Read on.

## What is a recipe?

A Syntask recipe is like a cookbook recipe: it tells you what you need &mdash; the ingredients &mdash; and some basic steps, but assumes you can put the pieces together. Think of the Hello Fresh meal experience, but for dataflows.

A tutorial, on the other hand, is Julia Child holding your hand through the entire cooking process: explaining each ingredient and procedure, demonstrating best practices, pointing out potential problems, and generally making sure you can’t stray from the happy path to a delicious meal.

We love Julia, and we love tutorials. But we don’t expect that a Syntask recipe should handhold users through every step and possible contingency of a solution. A recipe can start from an expectation of more expertise and problem-solving ability on the part of the reader.

To see an example of a high quality recipe, check out **[Serverless with AWS Chalice](https://github.com/Synopkg/syntask-recipes/tree/main/flows-advanced/serverless)**. This recipe includes all of the elements we like to see.

## Steps to add your recipe

Here’s our guide to creating a recipe:

<div class="terminal">
```bash
# Clone the repository
git clone git@github.com:Synopkg/syntask-recipes.git
cd syntask-recipes

# Create and checkout a new branch

git checkout -b new_recipe_branch_name

```
</div>

1. [Add your recipe](#what-are-the-common-ingredients-of-a-good-recipe). Your code may simply be a copy/paste of a single Python file or an entire folder. Unsure of where to add your file or folder? Just add under the `flows-advanced/` folder. A Syntask Recipes maintainer will help you find the best place for your recipe. Just want to direct others to a project you made, whether it be a repo or a blogpost? Simply link to it in the [Syntask Recipes README](https://github.com/Synopkg/syntask-recipes#readme)!
2. (Optional) Write a [README](#what-are-some-tips-for-a-good-recipe-readme).
3. Include a dependencies file, if applicable.
4. Push your code and make a PR to the repository.

That’s it! 

## What makes a good recipe?

Every recipe is useful, as other Syntask users can adapt the recipe to their needs. Particularly good ones help a Syntask user bake a great dataflow solution! Take a look at the [syntask-recipes repo](https://github.com/Synopkg/syntask-recipes) to see some examples.

## What are the common ingredients of a good recipe?

- Easy to understand: Can a user easily follow your recipe? Would a README or code comments help? A simple explanation providing context on how to use the example code is useful, but not required. A good README can set a recipe apart, so we have some additional suggestions for README files below.
- Code and more: Sometimes a use case is best represented in Python code or shell scripts. Sometimes a configuration file is the most important artifact &mdash; think of a Dockerfile or Terraform file for configuring infrastructure.
- All-inclusive: Share as much code as you can. Even boilerplate code like Dockerfiles or Terraform or Helm files are useful. Just *don’t share company secrets or IP*.
- Specific: Don't worry about generalizing your code, aside from removing anything internal/secret! Other users will extrapolate their own unique solutions from your example.

## What are some tips for a good recipe README?

A thoughtful README can take a recipe from good to great. Here are some best practices that we’ve found make for a great recipe README:

- Provide a brief explanation of what your recipe demonstrates. This helps users determine quickly whether the recipe is relevant to their needs or answers their questions.
- List which files are included and what each is meant to do. Each explanation can contain only a few words.
- Describe any dependencies and prerequisites (in addition to any dependencies you include in a requirements file). This includes both libraries or modules and any services your recipes depends on.
- If steps are involved or there’s an order to do things, a simple list of steps is helpful.
- Bonus: troubleshooting steps you encountered to get here or tips where other users might get tripped up.

## Next steps

We hope you’ll feel comfortable sharing your Syntask solutions as recipes in the [syntask-recipes repo](https://github.com/Synopkg/syntask-recipes#contributions). Collaboration and knowledge sharing are defining attributes of our [Syntask Community](https://www.syntask.io/slack)! 

Have questions about sharing or using recipes? Reach out on our active [Syntask Slack Community](https://www.syntask.io/slack)!

Happy engineering!
