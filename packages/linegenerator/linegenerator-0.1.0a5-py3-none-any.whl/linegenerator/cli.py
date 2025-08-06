import click

@click.command()
@click.option('--template', '-t', help='Template string')
@click.option('--lines', '-l', default=10, help='Number of lines to generate')
def main(template, lines):
    """Generate log lines."""
    click.echo(f"Generating {lines} log lines")
    if template:
        click.echo(f"Using template: {template}")
    else:
        click.echo("Using default template")

if __name__ == '__main__':
    main()