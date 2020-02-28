from yggdrasil_crawler import YggdrasilCrawler

class CrawlerCTL():

    crawler = None

    def __init__(self):
        self.crawler = YggdrasilCrawler()
        self.crawler.crawl()

    def print_table(self, table):
        longest_cols = [
            (max([len(str(row[i])) for row in table]) + 3)
            for i in range(len(table[0]))
        ]
        row_format = "".join(["{:>" + str(longest_col) + "}" for longest_col in longest_cols])
        for row in table:
            print(row_format.format(*row))

    def print_results(self):
        print("= = = = = AVAILABLE NODES = = = = =")
        node_list = [["NAME", "ADDRESS"]]
        for addr, nodeinfo in self.crawler.visited.items():
            #addr_splitted = addr.split(":")
            node_name = nodeinfo.get("name")
            node_list.append([node_name if node_name else "UNNAMED", addr])
        self.print_table(node_list)
        if len(self.crawler.timedout) > 0:
            print("= = = = = TIMEOUT NODES = = = = =")
            node_list = [["ADDRESS"]]
            for addr, nodeinfo in self.crawler.timedout.items():
                node_list.append([addr])
            self.print_table(node_list)
        print("= = = = = = = = = = = = = = = = =")
    
    def filter_nodes(self, data_filter):
        for addr, nodeinfo in self.crawler.visited.items():
            if data_filter in addr or data_filter in nodeinfo.get("name", ""):
                print(f'NODE INFO ({nodeinfo.get("name")}, {addr})')
                self.print_detailed_info(nodeinfo)

    def print_detailed_info(self, node_info):
        for k,v in node_info.items():
            print(f'  {k}={v}')

if __name__ == "__main__":
    crawlerctl = CrawlerCTL()
    crawlerctl.print_results()
    print("type 'h' for help")

    while True:
        user_input = input()

        if user_input.lower() == "q":  # quit
            break
        elif user_input.lower() == "h":
            print("'h' - help")
            print("'i NODE' - get detailed information about NODE, where NODE argument is either full name or address of target node")
            print("    or part of name/address to filter the list")
            print("'u' - update node list")
            print("'q' - quit")
        elif user_input.lower().startswith('i'):
            print(f"Filter: '{user_input[2:]}'")
            crawlerctl.filter_nodes(user_input[2:])
        elif user_input.lower() == "u":
            crawlerctl.crawler.crawl()
            crawlerctl.print_results()
        else:
            print(f"unknown command '{user_input}'")
