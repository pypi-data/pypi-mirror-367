
def parallel_run(cin,cases_to_plot,plot_pages,sub_plots,plot_vars,plot_defaults, error_bands,sub_plots_original):
    from .plot_driver import parallel_plotting
    parallel_plotting(cin,cases_to_plot,plot_pages,sub_plots,plot_vars,plot_defaults, error_bands,sub_plots_original)