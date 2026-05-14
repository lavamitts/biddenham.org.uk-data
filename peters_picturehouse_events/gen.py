import pyperclip


def generate_wp_clipboard_content():
    # Constructing a complex layout with native block comments
    # 1. A Heading Block
    # 2. A Group Block containing a Paragraph and an Image

    blocks = [
        "<!-- wp:heading -->",
        '<h2 class="wp-block-heading">Generated via Python</h2>',
        "<!-- /wp:heading -->",
        "<!-- wp:paragraph -->",
        "<p>This content was injected directly into your clipboard as a <strong>native block</strong>.</p>",
        "<!-- /wp:paragraph -->",
        '<!-- wp:image {"sizeSlug":"large","linkDestination":"none"} -->',
        '<figure class="wp-block-image size-large">',
        '<img src="https://via.placeholder.com/800x400" alt="Placeholder Image"/>',
        "</figure>",
        "<!-- /wp:image -->",
        "<!-- wp:columns -->",
        '<div class="wp-block-columns">',
        "<!-- wp:column -->",
        '<div class="wp-block-column"><!-- wp:paragraph --><p>Left column text.</p><!-- /wp:paragraph --></div>',
        "<!-- /wp:column -->",
        "<!-- wp:column -->",
        '<div class="wp-block-column"><!-- wp:paragraph --><p>Right column text.</p><!-- /wp:paragraph --></div>',
        "<!-- /wp:column -->",
        "</div>",
        "<!-- /wp:columns -->",
    ]

    # Join the blocks with newlines
    final_payload = "\n\n".join(blocks)

    # Send to clipboard
    pyperclip.copy(final_payload)
    print("WordPress blocks are now in your clipboard. Paste into WP now.")


if __name__ == "__main__":
    generate_wp_clipboard_content()
