# supermeals
Construct a meal that fits your Macros!!!

# Hi Noel
This README is to provide you with a bit of context, with the hopes that the code  
becomes more readable / understandable.  Please ignore the nginx, letsencrypt, and all other docker stuff.  
I'm still making some decisions regarding these, so they don't represent a working state.  And finally,  
I use postgres and make use of some of django's postres full text search functionality. This means  
that doing a quick switch to sqlite3 will not work a.k.a, you will have to use postgres if you  
want to test the site locally. You shouldn't need to do that because the site is live at  
macrobatics.xyz.  Use **username: vip**, and **password: vippass** to access the site.  

# Caveat
This is a personal project spannig over 2 years of on / off dev.  This means there are things needing refactoring,  
some model changes (Ingredients Model has redundant field in it for example), functions to simplify, more documentation etc.  
If you are curious about certain design decisions (or lack thereof) I would love to discuss them in more detail.  
The current site is what I would consider an MVP.

# Project Purpose
The idea behind this project was to allow a user to create meals that fit their nutritional goals,  
more specifically their desired macronutrient ratios i.e percentages of fat, carbs, protein.

# DB Schema
I think that more than anything, knowing the thought process behind the DB will illuminate the code in  
the views, models, and forms.  The main models to be concerned with are Foods, Ingredients, and Servings.  
A meal/recipe can be constructed by combining the Foods, Ingredient, and Servings models.  For example, say you    
construct a combination of peanut butter and bananas that will be 300 cals.  The way that appears  
in the DB would be something like the following (using dummy values):

### Tables Prior to Peanut Butter and Banana Combo Creation

**Foods Table**  

name | cals_per_gram
--- | ---
peanut butter | 6.0
banana | 2.0

**Servings**

description | quantity | grams | food(FK to Foods)
--- | --- | --- | ---
tbsp | 1 | 16 | peanut butter pk
cup | 1 | 32 | banana pk

### Tables After Peanut Butter and Banana Combo Creation

**Foods Table**  

name | cals_per_gram
--- | ---
peanut butter | 6.0
banana | 2.0
Your new peanut butter and bananas | 4.0

**Servings**

description | quantity | grams | food(FK to Foods)
--- | --- | --- | ---
tbsp | 1 | 16 | peanut butter pk
cup | 1 | 32 | banana pk
cup | 1 | 40 | your new peanut butter and bananas pk

**Ingredients**

main_food(FK to Foods) | ingredient(FK to Foods) | serving(FK to servings) | amount
--- | --- | --- | ---
your new peanut butter and bananas pk | peanut butter pk | peanut butter - tbsp pk | 2
your new peanut butter and bananas pk | bananas pk | bananas - cup pk | 0.75
