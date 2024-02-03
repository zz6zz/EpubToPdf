import pdfkit
import os
import multiprocessing
from pypdf import PdfMerger
from pypdf.errors import PdfReadError


class PdfEngine(object):

    """
        This class carries operations on pdf files.

        It has the following methods:

        convert() --- Which converts each of the markup file
        passed in to pdf. Markup file should be html

        combine() --- Which merges all of the pdf files created by
        the convert method, creating a new file.

        del_pdf() --- Which deletes all the pdf files created by
        the convert method.

    """

    def __init__(self, markup_files, style_files, pdf_files, directory):
        self.markup_files = markup_files
        self.style_files = style_files
        self.pdf_files = pdf_files
        self.directory = directory

    def convert(self):
        for each in self.markup_files:

            # For handle error:ProtocolUnknownE
            # options={'encoding': 'utf-8',"enable-local-file-access":True}
            options={"enable-local-file-access":True}
            try:
                pdfkit.from_file(each, "{}.pdf".format(self.markup_files.index(each)),
                                options=options)
            except Exception as e:
                # https://blog.csdn.net/seanblog/article/details/78884920
                # css use external resourse may cause:
                # Exit with code 1 due to network error: ContentNotFoundError
                print("converting: ", each,"-->", "{}.pdf".format(self.markup_files.index(each)))
                print(repr(e))
                input("press 'enter' to skip exception, 'Ctrl-C to shut down.")
                pass

        print('--- Sections converted to pdf')
    
    def batch_convert(self,in_out_dict: dict):
        for in_file, out_file in in_out_dict.items():
            # For handle error:ProtocolUnknownE
            options={'encoding': 'utf-8',"enable-local-file-access":True}
            try:
                pdfkit.from_file(in_file, out_file, options=options)
            except Exception as e:
                # https://blog.csdn.net/seanblog/article/details/78884920
                # css use external resourse may cause:
                # Exit with code 1 due to network error: ContentNotFoundError
                print("converting: ", in_file,"-->", out_file)
                print("skip:", repr(e))
                # input("press 'enter' to skip exception, 'Ctrl-C to shut down.")
                pass

    def multi_process_convert(self):
        process_cnt = 10
        batch_cnt = int((len(self.markup_files)+process_cnt-1)/process_cnt)
        process_load = {}
        for i in range(0,process_cnt):
            process_load[i]= {}
        for i in range(0, len(self.markup_files)):
            # map: input file --> output file
            process_load[int(i/batch_cnt)][self.markup_files[i]] = "{}.pdf".format(i)
        all_process = []
        for k,v in process_load.items():
            sub_process = multiprocessing.Process(target=self.batch_convert,kwargs={'in_out_dict':v})
            sub_process.start()
            all_process.append(sub_process)

        for p in all_process:
            p.join()

    def combine(self):

        merger = PdfMerger()

        for pdf in self.pdf_files:
            try:
                # merger.append(pdf, import_outline=False)
                merger.append(pdf, import_outline=True)
            except PdfReadError:
                pass

        merger.write("{}.pdf".format(self.directory))

        print('--- Sections combined together in a single pdf file')

        merger.close()

    def del_pdf(self):
            for each in self.pdf_files:
                os.remove(each)
            print('--- Individual pdf files deleted from directory')
