import json, sys, os, markdown, pdfkit
from mdx_gfm import GithubFlavoredMarkdownExtension


def main(args):
    input_path = args[0]
    output_path = input_path

    if len(args) > 1 and args[1] != '--debug':
        output_path = args[1]

    validate_path(input_path, 'input')
    validate_path(output_path, 'output')

    config = get_config('./config.json')
    users = config["users"]
    projects = config["projects"]
    active = config["active_projects"]

    if output_path[-1] != '/':
        output_path += '/'

    for ap in active:
        print('Collecting project [{}]'.format(ap))
        for count, user in enumerate(users):
            u = user[0] # uid
            n = user[1] # name
            print('\n  [{:02d}] {} ({}@calpoly.edu)'.format(count+1, n.upper(), u))
            sys.stdout.flush()
            for f in projects[ap]:
                print('    {} '.format(f), end='\t\t> ')
                sys.stdout.flush()

                html_path = output_path + 'html/{}_{}.html'.format(u, f)
                outline_file = None

                try:
                    outline_file = open('../data/submissions/{}/{}/{}'.format(ap, u, f),
                                        'r', encoding='UTF-8')
                except FileNotFoundError as e:
                    quote_index = str(e).find("'..")
                    print('SUBMISSION NOT FOUND {}'.format(str(e)[quote_index:]))

                if outline_file:
                    print('oln', end='')
                    sys.stdout.flush()

                    outline_content = preprocess(outline_file.readlines())
                    html_success = write_html(html_path, outline_content)
                    if html_success:
                        print(' html', end='')
                        sys.stdout.flush()
                    else:
                        print('    Failed to write \'{}\'\nCheck permissions?'.format(html_path),
                              file=sys.stderr, end='\n\n')

                    pdf_path = output_path + 'pdf/{}_{}.pdf'.format(u, f)
                    pdf_success = write_pdf(pdf_path, html_path)
                    if pdf_success:
                        print(' pdf', end='')
                        sys.stdout.flush()
                    else:
                        print('    Failed to write \'{}\'\n'.format(pdf_path) +
                              '    Check permissions or wkhtmltopdf availability.',
                              file=sys.stderr, end='\n\n')

                    if html_success and pdf_success:
                        print(' - OK')
                        sys.stdout.flush()


def validate_path(path, type='?'):
    if not os.path.isdir(path):
        print('Path given is invalid: {} ({})'.format(path, type), file=sys.stderr)
        exit(1)


def preprocess(lines):
    output = ''
    for line in lines:
        line_strip = line.strip()
        if line_strip:
            if line_strip[0] == '#':
                hash_index = line.find('#', 1)
                if line and line[hash_index + 1] != ' ':
                    line = line.replace('#', '# ', 1)
                if hash_index == 0:
                    line = ' ' + line
                output += line.replace('#', '-', 1)
            elif line_strip[0] == '|':
                output += '...' + line
            elif '"""' in line:
                output += '\n'
            else:
                output += line if output.strip() else '##' + line

    return output


def write_html(html_path, outline_content):
    try:
        oln_re_file = open(html_path.replace('.html', '').replace('.oln.py', '.oln.txt'),
                           'w', encoding='UTF-8')
        oln_re_file.writelines(outline_content)

        html_file = open(html_path, 'w', encoding='UTF-8')
        html_content = markdown.markdown(outline_content,
                                         extensions=[GithubFlavoredMarkdownExtension()])
        html_file.write('<html>\n<head><link rel="stylesheet" href="github.css"></head>\n')
        html_file.writelines(html_content)
        html_file.write('\n</html>\n')

        oln_re_file.close()
        html_file.close()
    except IOError:
        return False
    return True


def write_pdf(pdf_path, html_path):
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'dpi': 350,
        'quiet': ''
    }

    try:
        pdfkit.from_file(html_path, pdf_path, options=options)
    except IOError:
        return False
    return True


def get_config(json_path):
    return json.load(open(json_path))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 collect <path_to_code_outline_source> [path_to_generated_output]', end='\n\n')
        print('    when path_to_generated_output_source is optional; path_to_code_outline_source is used.', end='\n\n')
    else:
        main(sys.argv[1:])
