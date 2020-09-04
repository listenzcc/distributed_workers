# %%
import os

# Get log files in current folder
files = [e for e in os.listdir('.') if e.endswith('.log')]
files

# %%


class HTML(object):
    # Quickly make-up of a html file
    # 1. Use `print_header` to initial the html file, named as [self.fname];
    # 2. Use `open_dom` and `close_dom` to print wrapper of HTML dom,
    #    like <div> xxx </div>, ...,
    #    designed structure is
    #    <body>
    #     |--<div>
    #         |--<p>
    #         |--<p>
    #         |--<ul>
    #             |--<li>
    #             |--<li>
    #             |--<ol>
    #                 |--<li>
    #                 |--<li>
    #             |--</ol>
    #         |--</ul>
    #     |--</div>
    #    </body>
    # 3. Use `_append` to print content into the html file;
    # 4. Use `close_all` to close all the unclosed dom;

    def __init__(self, fname='index.html'):
        self.fname = fname
        print(f'Init new html: {fname}')

    def print_header(self, title='Title'):
        # Print header for the html file
        # User can assign the [title]
        # Use style.css in current folder
        with open(self.fname, 'wb') as f:
            f.writelines([e.encode() for e in ['<html>',
                                               '<head>',
                                               f'<title>{title}</title>',
                                               '<link rel="stylesheet" href="style.css" />',
                                               '</head>',
                                               '<body>',
                                               '\n']])

        # Init unclosed_count
        self.unclosed_count = dict(
            ol=0,
            ul=0,
            div=0,
            body=1,
            html=1,
        )

        print(f'Print <header> in {self.fname}')

    def close_all(self):
        # Safely close all the doms,
        # make sure the doms are closed in order
        for dom in ['ol', 'ul', 'div', 'body', 'html']:
            for _ in range(self.unclosed_count[dom]):
                self.close_dom(dom)

        print(f'Close safely to {self.fname}')

    def _append(self, lines):
        # Built-in method for appending new lines
        with open(self.fname, 'ab') as f:
            f.writelines([e.encode() for e in lines])
        print(f'Append lines: {len(lines)}')

    def open_dom(self, dom='div'):
        # Open a dom
        # Append dom starter
        self._append(['\n', f'<{dom}>', '\n'])
        # Increase counting
        self.unclosed_count[dom] += 1

    def close_dom(self, dom='div'):
        # Close the dom
        if self.unclosed_count[dom] > 0:
            # Only close it when counting is larger than 0
            self._append([f'</{dom}>', '\n', '\n'])
            # Decrease counting
            self.unclosed_count[dom] -= 1

    def append(self, lines):
        # Append new lines
        if isinstance(lines, str):
            # If the lines is str,
            # make it a list
            lines = [lines]

        if not lines[-1] == '\n':
            # Make sure the list ends with '\n'
            lines.append('\n')

        # Append using built-in _append method
        self._append(lines)


# %%
for fname in files:
    html = HTML(fname=f'{fname}.html')
    html.print_header(fname)

    with open(fname, 'r') as f:
        while True:
            line = f.readline()
            if len(line) == 0:
                break

            if ' - BCI - DEBUG - ' not in line:
                # Main filter
                # Ignore the lines not containing 'BCI DEBUG'
                continue

            if any([e in line.lower() for e in ['query', 'caiji']]):
                # Content filter
                # Only deal with the lines that contains 'query' and 'caiji'
                print(line)

                if 'Workload starts online_kaishicaiji' in line:
                    # Deal with kaishicaiji lines
                    # It should be a new <ul> in a new <div>
                    # Close <ul> and <div> in order
                    html.close_dom('ul')
                    html.close_dom('div')

                    # New <div> and <ul> in order
                    html.open_dom('div')
                    html.open_dom('ul')

                    # New <li> of line
                    html.append(['<li>', line, '</li>'])
                    continue

                if 'Received b\'{"mode":"Query"' in line:
                    # Deal with Query lines
                    # It should be a new <li> in existing <ul>
                    # Following lines of the Query should be <li>s in a new <ol>
                    # Close <ol>
                    html.close_dom('ol')

                    # New <li> of line
                    html.append(['<li>', line, '</li>'])

                    # New <ol> for following lines
                    html.open_dom('ol')
                    continue

                # Trivial <li> for lines in Query
                html.append(['<li>', line, '</li>'])

    # Safely close all doms
    html.close_all()

print('--Done--')

# %%
