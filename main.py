from MainWindow import MainWindow
import argparse


def parse():
    parser = argparse.ArgumentParser(description='Sigra Plot')

    parser.add_argument('-pathrun', type=str, action='append', nargs='+',
                        help='Path of file need to be plotted. (-path <filepath> {<filepath>})')

    parser.add_argument('-path', type=str, action='append', nargs='+',
                        help='Path of file need to be plotted. (-path <filepath> {<filepath>})')

    parser.add_argument('-title', type=str, nargs='+',
                        help='Set plot title. (-title <title name>)')

    parser.add_argument('-xaxis', type=str, nargs='+',
                        help='Set x axis label. (-xaxis <label name>)')

    parser.add_argument('-yaxis', type=str, nargs='+',
                        help='Set y axis label. (-yaxis <label name>)')

    parser.add_argument('-channel', type=int, action='append', nargs='+',
                        help='Select which channels be displayed. (-channel <channel number> {<channel number>})')

    parser.add_argument('-legend', type=str, action='append', nargs='+',
                        help='Set legends for the plot. (-legend <legend label> { , <legend label>})')

    parser.add_argument('-legendvis', type=int,
                        help='Show/Hide Legend. (-legendvis <1/0>)')

    parser.add_argument('-yrange', type=int, nargs=2,
                        help='Set range for y axis. (-yrange <min> <max>)')

    parser.add_argument('-xrange', type=str, nargs=2,
                        help='Set range for x axis. #x_start, x_end (-xrange <min> <max>)')

    parser.add_argument('-export', type=str,
                        help='Export plot to PNG file. (-export <filename>)')

    parser.add_argument('-setting', type=str,
                        help='Import setting from file. (-setting <filename>)')

    return parser.parse_args()


def main():
    args = parse()
    main_window = MainWindow()
    main_window.init_window()

    if args.legendvis is not None:
        main_window.show_hide_legend(args.legendvis)

    if args.pathrun is not None:
        if args.pathrun[0] is not None:
            for i in range(len(args.pathrun[0])):
                main_window.import_new_data(args.pathrun[0][i])
                main_window.exec()
                return

    if args.path is not None:
        if args.path[0] is not None:
            for i in range(len(args.path[0])):
                main_window.import_new_data(args.path[0][i])
    else:
        main_window.exec()
        return

    if args.channel is not None:
        if args.channel[0] is not None:
            main_window.set_channel_vis(args.channel[0])
    if args.yrange is not None:
        main_window.set_y_range(args.yrange[0], args.yrange[1])
    if args.xrange is not None:
        main_window.set_x_range(args.xrange[0], args.xrange[1])
    if args.title is not None:
        main_window.set_title(' '.join(args.title))
    if args.xaxis is not None:
        main_window.set_x_axis(' '.join(args.xaxis))
    if args.yaxis is not None:
        main_window.set_y_axis(' '.join(args.yaxis))
    if args.legend is not None:
        if args.legend[0] is not None:
            ls = ' '.join(args.legend[0]).split(',')
            main_window.set_legends(ls)

    if args.setting is not None:
        main_window.import_setting_file(args.setting)

    if args.export is not None:
        main_window.export_image(args.export)


if __name__ == '__main__':
    main()
