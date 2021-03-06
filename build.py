#!/usr/bin/python3
# encoding: utf-8

import sys, math, os, shutil


def get_contents(filename):
    with open("./recipe/" + filename) as f:
        return f.readlines()


if not os.path.exists("build"):
    os.makedirs("build")

for f in os.listdir("build"):
    path = os.path.join("build", f)
    try:
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)
    except Exception as e:
        print("Failed to clear build dir. %s" % (path, e))

recipes = [
    f for f in os.listdir("recipe")
    if os.path.isfile(os.path.join("recipe", f))
]

if (len(recipes) < 1):
    print("No recipes found in ./recipe")
    sys.exit()

print("Found", len(recipes), "valid recipes. Building...")

recipesBuilt = 0

for i in range(0, len(recipes)):

    #----------------------get info from file and make build html

    content = get_contents(recipes[i])

    # This section is looking for an asciidoc file structured like this:
    # Header looks like this:     "= [Name]"
    # Ingredients look like this: "* [Name]"
    # Steps look like this:       ". [Name]"

    needsName = True
    needsIngredients = True
    needsSteps = True

    ingredients = []
    steps = []
    filename = recipes[i][:-3]

    for j in range(0, len(content)):

        if (content[j].startswith("= ")):  # The name of the recipe
            recipeName = content[j][2:].replace('\n', '')
            needsName = False

        if (content[j].startswith("* ")):  # An ingredient
            ingredients.append(content[j][2:].replace('\n', ''))
            needsIngredients = False

        if (content[j].startswith(". ")):  # A step in the recipe
            steps.append(content[j][2:].replace('\n', ''))
            needsSteps = False

    if needsName or needsIngredients or needsSteps:
        print("This isn't a valid recipe!")
        continue  # skip over this file and continue

    shutil.copy2("./template/recipe.html", "./build/" + filename + ".html")

    pageNumber = math.floor(i / 15) + 1

    #---------------------modify file

    with open("./build/" + filename + ".html", "r+") as f:
        raw = f.read()

        raw = raw.replace('[recipe-name]', recipeName)

        raw = raw.replace('[recipe-path]', filename)

        raw = raw.replace('[page-num]', str(pageNumber))

        recipeIngredients = ""
        for i in range(0, len(ingredients)):
            recipeIngredients += "<li>" + ingredients[i] + "</li>\n"
        raw = raw.replace('[recipe-ingredients]', recipeIngredients)

        recipeSteps = ""
        for i in range(0, len(steps)):
            recipeSteps += "<li>" + steps[i] + "</li>\n"
        raw = raw.replace('[recipe-steps]', recipeSteps)

        f.seek(0)
        f.write(raw)
        f.truncate()

    recipesBuilt += 1

    #----------------------handling for homepage

    if not os.path.isfile("./build/home" + str(pageNumber) + ".html"):
        shutil.copy2("./template/home.html",
                     "./build/home" + str(pageNumber) + ".html")

    with open("./build/home" + str(pageNumber) + ".html", "r+") as f:
        raw = f.read()

        cardTemplate = """
        <div class="col-lg-4">
        <a href="[recipe-path].html" class="card-link">
            <div class="card mb-3">
            <div class="card-highlight"></div>
            <img class="card-image" src="img/[recipe-path].jpg" alt="[recipe-name]" />
            <h4 class="card-header">[recipe-name]</h4>
            </div>
        </a>
        </div>
        <!--Add cards here!-->
        """

        card = cardTemplate.replace("[recipe-path]", filename)

        card = card.replace('[recipe-name]', recipeName)

        raw = raw.replace("<!--Add cards here!-->", card)

        f.seek(0)
        f.write(raw)
        f.truncate()

totalPages = math.floor(recipesBuilt / 15) + 1

for i in range(1, totalPages + 1):  #+1 to both sides for ease

    #---------------------- dealing with pagination

    print("Cleaning up built homepages...")

    with open("./build/home" + str(i) + ".html", "r+") as f:
        raw = f.read()

        if (i == 1):
            # the first page will never have a page to it's left
            raw = raw.replace("[is-left-disabled]", "disabled")
        else:
            raw = raw.replace("[page-left]", "home" + str(i - 1) + ".html")

        if (i == totalPages):
            raw = raw.replace("[is-right-disabled]", "disabled")
        else:
            raw = raw.replace("[page-right]", "home" + str(i + 1) + ".html")

        raw = raw.replace("[page-num]", str(i))

        f.seek(0)
        f.write(raw)
        f.truncate()

    #------------------------ copy images to build folder

    shutil.copytree("./img", "./build/img")

print("Done!")
