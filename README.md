# GynxLife-API
Your commits are life. Literally.

GynxLife-API transforms your GitHub contribution history (the 52-week grid) into a living simulation of Conway's Game of Life. Every commit acts as a seed that interacts with its neighbors to create unique, evolving evolutionary patterns.

<p>
    <img src="https://g-lyfe-api.vercel.app/api/seed.png?pattern=random" alt="GynxLife Evolution Seed" width="600">
    <img src="https://g-lyfe-api.vercel.app/api/life.gif?pattern=random" alt="GynxLife Evolution" width="600">
</p>

# Quick Start

No installation required. Simply add this URL to your GitHub Profile README:

https://g-lyfe-api.vercel.app/api/life.gif?user=YOUR_USERNAME&color=HEX_COLOR

    user: Your GitHub username.
    color: Hexadecimal color for the cells (e.g., bb9af7 for neon purple). Do not include the # symbol in the URL.

# How the GofLyfe Engine Works

This project translates technical activity into artificial biological rules. Here is the logic behind the simulation:

1. The Canvas (52x7 Grid)

Unlike traditional Game of Life setups, GynxLife uses the exact geometry of GitHub's contribution graph: 52 columns (weeks) by 7 rows (days).

2. Toroidal Universe (Wrapping)

To prevent "life" from dying at the edges, we implemented Modulo (%) logic. If a cell exits through the right, it reappears on the left. This creates a seamless, infinite-feeling simulation.

3. The Golden Rules

The engine evaluates each cell based on its 8 immediate neighbors:

    Survival: A live cell with 2 or 3 neighbors stays alive.

    Death: Fewer than 2 neighbors (solitude) or more than 3 (overpopulation) kills the cell.

    Birth: An empty space with exactly 3 neighbors "gives birth" to a new cell.

# Deploy Your Own Instance

If you want to run this under your own domain and token:

    Clone this repository.

    Generate a PAT (Personal Access Token): In GitHub Settings > Developer Settings with the read:user permission.

    Environment Variables: Configure GITHUB_TOKEN in your Vercel dashboard.

    Deploy: Run vercel --prod or connect your GitHub repository to Vercel for automatic CI/CD.


<p>
  <i>"Everything is a system, you just have to find the logic behind it."</i>
  <br>
  <b>— LDGnx</b>
</p>
