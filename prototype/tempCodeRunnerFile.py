def create_monthly_graph(csv_file_path, graph_path):
#     df = pd.read_csv(csv_file_path)
#     df["Date"] = pd.to_datetime(df["Date"], format="%b %d, %Y", errors="coerce")
#     df = df.dropna(subset=["Date"])
#     df["Month"] = df["Date"].dt.to_period("M")
#     monthly_summary = df.groupby(["Month", "Type"])["Amount"].sum().unstack(fill_value=0)

#     monthly_summary.plot(
#         kind="bar",
#         figsize=(10, 6),
#         stacked=True,
#         color=["red", "green"],
#         title="Monthly Transaction Overview"
#     )
#     plt.xlabel("Month")
#     plt.ylabel("Amount")
#     plt.xticks(rotation=45, ha="right")
#     plt.legend(["Debits", "Credits"])
#     plt.tight_layout()
#     plt.savefig(graph_path)
#     plt.close()