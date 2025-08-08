#!/usr/bin/env python3
"""
TMDB CLI Tool - A command-line interface for The Movie Database API
"""

import os
import sys
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.columns import Columns
from rich import box
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()

# TMDB API configuration
API_KEY = os.getenv('API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'


def check_api_key():
    """Check if API key is available"""
    if not API_KEY:
        console.print(
            "[bold red]Error:[/bold red] API_KEY not found in .env file", style="red")
        console.print(
            "[yellow]Please create a .env file with your TMDB API key:[/yellow]")
        console.print(
            "[cyan]1. Visit https://www.themoviedb.org/settings/api[/cyan]")
        console.print(
            "[cyan]2. Create a .env file: echo 'API_KEY=your_api_key_here' > .env[/cyan]")
        sys.exit(1)


class TMDBClient:
    """Client for interacting with TMDB API"""

    def __init__(self):
        check_api_key()  # Check API key when client is created
        self.session = requests.Session()
        self.session.params = {'api_key': API_KEY}

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to TMDB API with error handling"""
        url = f"{BASE_URL}/{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            console.print(
                "[bold red]Error:[/bold red] Request timed out", style="red")
            return None
        except requests.exceptions.ConnectionError:
            console.print(
                "[bold red]Error:[/bold red] Connection failed. Please check your internet connection.", style="red")
            return None
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                console.print(
                    "[bold red]Error:[/bold red] Invalid API key", style="red")
            elif response.status_code == 404:
                console.print(
                    "[bold red]Error:[/bold red] Resource not found", style="red")
            else:
                console.print(
                    f"[bold red]Error:[/bold red] HTTP {response.status_code}: {e}", style="red")
            return None
        except Exception as e:
            console.print(
                f"[bold red]Error:[/bold red] Unexpected error: {e}", style="red")
            return None

    def search_movies(self, query: str, page: int = 1) -> Optional[Dict]:
        """Search for movies by title"""
        return self._make_request('search/movie', {'query': query, 'page': page})

    def get_trending_movies(self, time_window: str = 'day') -> Optional[Dict]:
        """Get trending movies for day or week"""
        return self._make_request(f'trending/movie/{time_window}')

    def get_upcoming_movies(self) -> Optional[Dict]:
        """Get upcoming movie releases"""
        return self._make_request('movie/upcoming')

    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Get detailed information for a specific movie"""
        return self._make_request(f'movie/{movie_id}')


def format_movie_list(movies: List[Dict], title: str) -> None:
    """Format and display a list of movies in a table"""
    if not movies:
        console.print(f"[yellow]No movies found for {title.lower()}[/yellow]")
        return

    table = Table(title=title, box=box.ROUNDED,
                  show_header=True, header_style="bold magenta")
    table.add_column("Title", style="cyan", width=30)
    table.add_column("Release Date", style="green", width=12)
    table.add_column("Rating", style="yellow", width=8)
    table.add_column("Overview", style="white", width=50)

    for movie in movies[:10]:  # Limit to 10 results
        title = movie.get('title', 'N/A')
        release_date = movie.get('release_date', 'N/A')
        if release_date and release_date != 'N/A':
            try:
                # Format date to be more readable
                date_obj = datetime.strptime(release_date, '%Y-%m-%d')
                release_date = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                pass

        rating = movie.get('vote_average', 0)
        rating_str = f"{rating:.1f}/10" if rating else "N/A"

        overview = movie.get('overview', 'No overview available')
        # Truncate overview to fit in table
        if len(overview) > 100:
            overview = overview[:97] + "..."

        table.add_row(title, release_date, rating_str, overview)

    console.print(table)

    if len(movies) > 10:
        console.print(f"[dim]Showing 10 of {len(movies)} results[/dim]")


def format_movie_details(movie: Dict) -> None:
    """Format and display detailed movie information"""
    title = movie.get('title', 'N/A')
    tagline = movie.get('tagline', '')

    # Create header with title and tagline
    header_text = f"[bold cyan]{title}[/bold cyan]"
    if tagline:
        header_text += f"\n[italic]{tagline}[/italic]"

    console.print(Panel(header_text, box=box.DOUBLE, padding=(1, 2)))

    # Basic information table
    info_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    info_table.add_column("Field", style="bold yellow", width=20)
    info_table.add_column("Value", style="white")

    # Add movie details
    release_date = movie.get('release_date', 'N/A')
    if release_date and release_date != 'N/A':
        try:
            date_obj = datetime.strptime(release_date, '%Y-%m-%d')
            release_date = date_obj.strftime('%B %d, %Y')
        except ValueError:
            pass

    info_table.add_row("Release Date", release_date)
    info_table.add_row(
        "Rating", f"{movie.get('vote_average', 0):.1f}/10 ({movie.get('vote_count', 0)} votes)")
    info_table.add_row(
        "Runtime", f"{movie.get('runtime', 'N/A')} minutes" if movie.get('runtime') else "N/A")
    info_table.add_row(
        "Budget", f"${movie.get('budget', 0):,}" if movie.get('budget') else "N/A")
    info_table.add_row(
        "Revenue", f"${movie.get('revenue', 0):,}" if movie.get('revenue') else "N/A")

    # Genres
    genres = movie.get('genres', [])
    genre_names = [genre['name'] for genre in genres] if genres else ['N/A']
    info_table.add_row("Genres", ", ".join(genre_names))

    # Production companies
    companies = movie.get('production_companies', [])
    company_names = [company['name']
                     for company in companies[:3]] if companies else ['N/A']
    info_table.add_row("Production", ", ".join(company_names))

    console.print(info_table)

    # Overview
    overview = movie.get('overview', 'No overview available')
    if overview and overview != 'No overview available':
        console.print(
            Panel(overview, title="[bold]Overview[/bold]", box=box.ROUNDED))


# Watchlist Management Functions
def get_watchlist_file():
    """Get path to watchlist file"""
    return Path.home() / ".tmdb_watchlist.json"


def load_watchlist():
    """Load watchlist from file"""
    watchlist_file = get_watchlist_file()
    if watchlist_file.exists():
        try:
            with open(watchlist_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_watchlist(watchlist):
    """Save watchlist to file"""
    watchlist_file = get_watchlist_file()
    try:
        with open(watchlist_file, 'w') as f:
            json.dump(watchlist, f, indent=2)
        return True
    except IOError:
        return False


def is_in_watchlist(movie_id):
    """Check if movie is in watchlist"""
    watchlist = load_watchlist()
    return any(movie['id'] == movie_id for movie in watchlist)


def add_to_watchlist(movie):
    """Add movie to watchlist"""
    watchlist = load_watchlist()
    if not is_in_watchlist(movie['id']):
        watchlist_movie = {
            'id': movie['id'],
            'title': movie['title'],
            'release_date': movie.get('release_date', ''),
            'rating': movie.get('vote_average', 0),
            'added_date': str(datetime.now().date())
        }
        watchlist.append(watchlist_movie)
        save_watchlist(watchlist)
        return True
    return False


def remove_from_watchlist(movie_id):
    """Remove movie from watchlist"""
    watchlist = load_watchlist()
    original_length = len(watchlist)
    watchlist = [movie for movie in watchlist if movie['id'] != movie_id]
    if len(watchlist) < original_length:
        save_watchlist(watchlist)
        return True
    return False


def create_movie_card(movie, index):
    """Create a rich movie card display"""
    title = movie.get('title', 'Unknown Title')
    release_date = movie.get('release_date', 'Unknown')
    rating = movie.get('vote_average', 0)
    overview = movie.get('overview', 'No overview available.')

    # Truncate overview
    if len(overview) > 100:
        overview = overview[:100] + "..."

    # Rating color
    rating_color = "green" if rating >= 7 else "yellow" if rating >= 5 else "red"

    # Check if in watchlist
    watchlist_status = "⭐" if is_in_watchlist(movie['id']) else "  "

    card_content = f"""[bold cyan]{index}. {title}[/bold cyan] {watchlist_status}
📅 {release_date} | ⭐ [{rating_color}]{rating}/10[/{rating_color}]
{overview}"""

    return Panel(card_content, border_style="blue", padding=(0, 1))


def show_movie_details(movie_id):
    """Show detailed movie information"""
    client = TMDBClient()
    movie = client.get_movie_details(movie_id)
    if movie:
        format_movie_details(movie)


def manage_watchlist(current_movies, start_idx):
    """Interactive watchlist management"""
    console.clear()
    console.print("\n🎬 [bold cyan]Watchlist Management[/bold cyan]\n")

    # Show current movies with numbers
    for i, movie in enumerate(current_movies, start_idx + 1):
        status = "⭐ [green]In Watchlist[/green]" if is_in_watchlist(
            movie['id']) else "[dim]Not in watchlist[/dim]"
        console.print(f"{i}. [cyan]{movie['title']}[/cyan] - {status}")

    console.print(f"\n📋 [bold]Commands:[/bold]")
    console.print("• [cyan]add <number>[/cyan] - Add movie to watchlist")
    console.print(
        "• [cyan]remove <number>[/cyan] - Remove movie from watchlist")
    console.print("• [cyan]show[/cyan] - Show full watchlist")
    console.print("• [cyan]back[/cyan] - Return to browser")

    while True:
        choice = Prompt.ask("\nWatchlist command",
                            default="back").lower().strip()

        if choice == 'back':
            break
        elif choice == 'show':
            show_watchlist()
        elif choice.startswith('add '):
            try:
                movie_num = int(choice.split()[1]) - 1 - start_idx
                if 0 <= movie_num < len(current_movies):
                    movie = current_movies[movie_num]
                    if add_to_watchlist(movie):
                        console.print(
                            f"[green]✓ Added '{movie['title']}' to watchlist![/green]")
                    else:
                        console.print(
                            f"[yellow]'{movie['title']}' is already in watchlist![/yellow]")
                else:
                    console.print("[red]Invalid movie number![/red]")
            except (ValueError, IndexError):
                console.print("[red]Invalid command! Use 'add <number>'[/red]")
        elif choice.startswith('remove '):
            try:
                movie_num = int(choice.split()[1]) - 1 - start_idx
                if 0 <= movie_num < len(current_movies):
                    movie = current_movies[movie_num]
                    if remove_from_watchlist(movie['id']):
                        console.print(
                            f"[green]✓ Removed '{movie['title']}' from watchlist![/green]")
                    else:
                        console.print(
                            f"[yellow]'{movie['title']}' was not in watchlist![/yellow]")
                else:
                    console.print("[red]Invalid movie number![/red]")
            except (ValueError, IndexError):
                console.print(
                    "[red]Invalid command! Use 'remove <number>'[/red]")


def show_watchlist():
    """Display the full watchlist"""
    watchlist = load_watchlist()

    if not watchlist:
        console.print("\n[yellow]Your watchlist is empty![/yellow]")
        console.print(
            "Use the [cyan]browse[/cyan] command to discover and add movies.")
        return

    console.print(
        f"\n📋 [bold cyan]Your Watchlist[/bold cyan] ({len(watchlist)} movies)\n")

    # Create watchlist table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Title", style="cyan", min_width=30)
    table.add_column("Release Date", style="green", width=12)
    table.add_column("Rating", style="yellow", width=8)
    table.add_column("Added", style="dim", width=12)

    for i, movie in enumerate(watchlist, 1):
        rating_color = "green" if movie['rating'] >= 7 else "yellow" if movie['rating'] >= 5 else "red"
        rating_display = f"[{rating_color}]{movie['rating']}/10[/{rating_color}]"

        table.add_row(
            str(i),
            movie['title'],
            movie['release_date'] or "Unknown",
            rating_display,
            movie['added_date']
        )

    console.print(table)

    # Watchlist management options
    console.print(f"\n💡 [bold]Options:[/bold]")
    console.print("• [cyan]details <number>[/cyan] - View movie details")
    console.print("• [cyan]remove <number>[/cyan] - Remove from watchlist")
    console.print("• [cyan]clear[/cyan] - Clear entire watchlist")
    console.print("• [cyan]export[/cyan] - Export watchlist to file")

    choice = Prompt.ask(
        "\nWatchlist action (or Enter to continue)", default="").lower().strip()

    if choice.startswith('details '):
        try:
            movie_num = int(choice.split()[1]) - 1
            if 0 <= movie_num < len(watchlist):
                show_movie_details(watchlist[movie_num]['id'])
                input("\nPress Enter to continue...")
        except (ValueError, IndexError):
            console.print("[red]Invalid command![/red]")
    elif choice.startswith('remove '):
        try:
            movie_num = int(choice.split()[1]) - 1
            if 0 <= movie_num < len(watchlist):
                movie = watchlist[movie_num]
                if Confirm.ask(f"Remove '{movie['title']}' from watchlist?"):
                    remove_from_watchlist(movie['id'])
                    console.print(
                        "[green]✓ Movie removed from watchlist![/green]")
        except (ValueError, IndexError):
            console.print("[red]Invalid command![/red]")
    elif choice == 'clear':
        if Confirm.ask("Clear entire watchlist?"):
            save_watchlist([])
            console.print("[green]✓ Watchlist cleared![/green]")
    elif choice == 'export':
        export_watchlist()


def export_watchlist():
    """Export watchlist to a file"""
    watchlist = load_watchlist()
    if not watchlist:
        console.print(
            "[yellow]Nothing to export - watchlist is empty![/yellow]")
        return

    filename = f"tmdb_watchlist_{datetime.now().strftime('%Y%m%d')}.txt"
    try:
        with open(filename, 'w') as f:
            f.write("🎬 TMDB Watchlist Export\n")
            f.write(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")

            for i, movie in enumerate(watchlist, 1):
                f.write(f"{i}. {movie['title']}\n")
                f.write(f"   Release Date: {movie['release_date']}\n")
                f.write(f"   Rating: {movie['rating']}/10\n")
                f.write(f"   Added to watchlist: {movie['added_date']}\n\n")

        console.print(f"[green]✓ Watchlist exported to '{filename}'![/green]")
    except IOError as e:
        console.print(f"[red]Error exporting watchlist: {e}[/red]")


# CLI Commands
@click.group()
@click.version_option(version='1.0.0', prog_name='tmdb-cli')
def cli():
    """
    TMDB CLI - A command-line tool for The Movie Database API

    Search for movies, get trending lists, upcoming releases, and detailed movie information.
    """
    pass


@cli.command()
@click.argument('query')
@click.option('--page', '-p', default=1, help='Page number for search results')
def search(query: str, page: int):
    """Search for movies by title"""
    if not query.strip():
        console.print("[red]Error: Search query cannot be empty[/red]")
        return

    client = TMDBClient()
    console.print(f"[bold blue]Searching for:[/bold blue] {query}")

    with console.status("[bold green]Fetching search results..."):
        data = client.search_movies(query, page)

    if data is None:
        return

    movies = data.get('results', [])
    total_results = data.get('total_results', 0)

    if total_results == 0:
        console.print(f"[yellow]No movies found for '{query}'[/yellow]")
        return

    format_movie_list(movies, f"Search Results for '{query}' (Page {page})")

    if total_results > len(movies):
        total_pages = data.get('total_pages', 1)
        console.print(
            f"\n[dim]Page {page} of {total_pages} | Total results: {total_results}[/dim]")
        if page < total_pages:
            console.print(
                f"[dim]Use --page {page + 1} to see more results[/dim]")


@cli.command()
@click.option('--type', 'time_window', default='day',
              type=click.Choice(['day', 'week']),
              help='Time window for trending movies')
def trending(time_window: str):
    """Fetch trending movies for the day or week"""
    client = TMDBClient()
    console.print(
        f"[bold blue]Fetching trending movies for the {time_window}...[/bold blue]")

    with console.status("[bold green]Loading trending movies..."):
        data = client.get_trending_movies(time_window)

    if data is None:
        return

    movies = data.get('results', [])
    format_movie_list(movies, f"Trending Movies ({time_window.capitalize()})")


@cli.command()
def upcoming():
    """Show upcoming movie releases"""
    client = TMDBClient()
    console.print("[bold blue]Fetching upcoming movie releases...[/bold blue]")

    with console.status("[bold green]Loading upcoming movies..."):
        data = client.get_upcoming_movies()

    if data is None:
        return

    movies = data.get('results', [])
    format_movie_list(movies, "Upcoming Movie Releases")


@cli.command()
@click.argument('movie_id', type=int)
def details(movie_id: int):
    """Fetch and display detailed info for a given movie ID"""
    if movie_id <= 0:
        console.print("[red]Error: Movie ID must be a positive integer[/red]")
        return

    client = TMDBClient()
    console.print(
        f"[bold blue]Fetching details for movie ID: {movie_id}[/bold blue]")

    with console.status("[bold green]Loading movie details..."):
        movie = client.get_movie_details(movie_id)

    if movie is None:
        return

    if 'success' in movie and movie['success'] is False:
        console.print(f"[red]Movie with ID {movie_id} not found[/red]")
        return

    format_movie_details(movie)


@cli.command()
@click.option('--category', type=click.Choice(['popular', 'top_rated', 'now_playing']),
              default='popular', help='Movie category to browse')
def browse(category):
    """🎬 Interactive movie browser with watchlist management"""
    client = TMDBClient()

    try:
        with console.status(f"[bold green]Loading {category} movies..."):
            data = client._make_request(f'movie/{category}')

        if data is None:
            return

        movies = data.get('results', [])
        if not movies:
            console.print("[yellow]No movies found.[/yellow]")
            return

        current_page = 0
        movies_per_page = 5

        while True:
            # Display current page of movies
            start_idx = current_page * movies_per_page
            end_idx = start_idx + movies_per_page
            current_movies = movies[start_idx:end_idx]

            console.clear()
            console.print(f"\n🎬 [bold cyan]{category.replace('_', ' ').title()} Movies[/bold cyan] "
                          f"(Page {current_page + 1}/{(len(movies) - 1) // movies_per_page + 1})\n")

            # Create movie cards
            for i, movie in enumerate(current_movies, start_idx + 1):
                movie_card = create_movie_card(movie, i)
                console.print(movie_card)

            # Interactive menu
            console.print("\n" + "="*60)
            console.print(
                "🎮 [bold]Commands:[/bold] [cyan]n[/cyan]ext | [cyan]p[/cyan]rev | [cyan]w[/cyan]atchlist | [cyan]d[/cyan]etails <num> | [cyan]q[/cyan]uit")

            choice = Prompt.ask("Enter command", default="n").lower().strip()

            if choice == 'q' or choice == 'quit':
                break
            elif choice == 'n' or choice == 'next':
                if end_idx < len(movies):
                    current_page += 1
                else:
                    console.print("[yellow]Already on last page![/yellow]")
                    input("Press Enter to continue...")
            elif choice == 'p' or choice == 'prev':
                if current_page > 0:
                    current_page -= 1
                else:
                    console.print("[yellow]Already on first page![/yellow]")
                    input("Press Enter to continue...")
            elif choice == 'w' or choice == 'watchlist':
                manage_watchlist(current_movies, start_idx)
            elif choice.startswith('d') and len(choice.split()) == 2:
                try:
                    movie_num = int(choice.split()[1]) - 1
                    if 0 <= movie_num < len(movies):
                        show_movie_details(movies[movie_num]['id'])
                        input("\nPress Enter to continue...")
                    else:
                        console.print("[red]Invalid movie number![/red]")
                        input("Press Enter to continue...")
                except ValueError:
                    console.print(
                        "[red]Invalid command format! Use 'd <number>'[/red]")
                    input("Press Enter to continue...")

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error fetching movies: {e}[/red]")


@cli.command()
def watchlist():
    """📋 Manage and view your personal watchlist"""
    show_watchlist()


@cli.command()
@click.option('--movie-id', type=int, help='Get recommendations based on a specific movie')
@click.option('--genre', help='Get recommendations by genre')
def recommend(movie_id, genre):
    """🎯 Get personalized movie recommendations"""
    client = TMDBClient()

    try:
        if movie_id:
            # Get recommendations based on a movie
            with console.status(f"[bold green]Finding movies similar to ID {movie_id}..."):
                data = client._make_request(
                    f'movie/{movie_id}/recommendations')

            if data is None:
                return

            movies = data.get('results', [])[:10]  # Limit to top 10

            if not movies:
                console.print(
                    "[yellow]No recommendations found for this movie.[/yellow]")
                return

            console.print(
                f"\n🎯 [bold cyan]Movies Similar to Movie ID {movie_id}[/bold cyan]\n")

        elif genre:
            # Get movies by genre
            with console.status(f"[bold green]Finding {genre} movies..."):
                # First get genre list to find ID
                genre_data = client._make_request('genre/movie/list')
                if genre_data is None:
                    return

                genres = genre_data.get('genres', [])

                genre_id = None
                for g in genres:
                    if genre.lower() in g['name'].lower():
                        genre_id = g['id']
                        break

                if not genre_id:
                    console.print(f"[red]Genre '{genre}' not found![/red]")
                    console.print("Available genres: " +
                                  ", ".join([g['name'] for g in genres]))
                    return

                # Get movies by genre
                params = {
                    'with_genres': genre_id,
                    'sort_by': 'popularity.desc'
                }
                data = client._make_request('discover/movie', params)

            if data is None:
                return

            movies = data.get('results', [])[:10]
            console.print(
                f"\n🎯 [bold cyan]Popular {genre.title()} Movies[/bold cyan]\n")

        else:
            # Get general recommendations based on watchlist
            watchlist = load_watchlist()
            if not watchlist:
                console.print(
                    "[yellow]Add movies to your watchlist first to get personalized recommendations![/yellow]")
                return

            console.print(
                "\n🎯 [bold cyan]Recommendations Based on Your Watchlist[/bold cyan]\n")
            # This is a simplified recommendation - in a real app you'd use more sophisticated logic
            movies = []
            for movie in watchlist[:3]:  # Use top 3 watchlist movies
                try:
                    data = client._make_request(
                        f'movie/{movie["id"]}/recommendations')
                    if data:
                        recommendations = data.get('results', [])
                        movies.extend(recommendations[:3])
                except:
                    continue

            # Remove duplicates and limit
            seen_ids = set()
            unique_movies = []
            for movie in movies:
                if movie['id'] not in seen_ids:
                    seen_ids.add(movie['id'])
                    unique_movies.append(movie)
                if len(unique_movies) >= 10:
                    break

            movies = unique_movies

        if not movies:
            console.print("[yellow]No recommendations found.[/yellow]")
            return

        # Display recommendations
        for i, movie in enumerate(movies, 1):
            title = movie.get('title', 'Unknown Title')
            release_date = movie.get('release_date', 'Unknown')
            rating = movie.get('vote_average', 0)
            overview = movie.get('overview', 'No overview available.')

            if len(overview) > 150:
                overview = overview[:150] + "..."

            rating_color = "green" if rating >= 7 else "yellow" if rating >= 5 else "red"
            watchlist_status = "⭐" if is_in_watchlist(movie['id']) else ""

            panel_content = f"""[bold cyan]{i}. {title}[/bold cyan] {watchlist_status}
📅 {release_date} | ⭐ [{rating_color}]{rating}/10[/{rating_color}]
{overview}

[dim]Movie ID: {movie['id']} | Use './tmdb details {movie['id']}' for more info[/dim]"""

            console.print(
                Panel(panel_content, border_style="green", padding=(0, 1)))

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error fetching recommendations: {e}[/red]")


if __name__ == '__main__':
    cli()
