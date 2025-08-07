import inspect

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class datavis:
    def __init__(self):
        """Initialize DataVis with default theme settings."""
        self.themes = {
            "default": {
                "template": "plotly_white",
                "colorscale": "viridis",
                "line_color": "#1f77b4",
                "background_color": "white",
                "grid_color": "lightgray",
                "text_color": "black",
                "font_family": "Raleway, sans-serif",
                "font_size": 12,
            },
            "dark": {
                "template": "plotly_dark",
                "colorscale": "plasma",
                "line_color": "#f07b16",
                "background_color": "#2f3136",
                "grid_color": "#1cd416",
                "text_color": "white",
                "font_family": "Raleway, sans-serif",
                "font_size": 12,
            },
            "business": {
                "template": "plotly_white",
                "colorscale": "blues",
                "line_color": "#0e4272",
                "background_color": "white",
                "grid_color": "#e6e6e6",
                "text_color": "#921919",
                "font_family": "Raleway, sans-serif",
                "font_size": 11,
            },
            "scientific": {
                "template": "plotly_dark",
                "colorscale": "rdylbu",
                "line_color": "#d62728",
                "background_color": "white",
                "grid_color": "#f0f0f0",
                "text_color": "black",
                "font_family": "Raleway, sans-serif",
                "font_size": 10,
            },
        }
        self.current_theme = "default"

    def help(self, method=None, *, show_examples=True):
        """
        Enhanced help system with detailed information about all methods.

        Parameters
        ----------
        method : str, optional
            Specific method to get help for. If None, shows overview of all methods.
        show_examples : bool, default True
            Whether to show usage examples.

        Usage:
        ------
        vis.help()                    # Show all methods
        vis.help('plot_one')          # Show help for specific method
        vis.help('plot_chart', show_examples=False) # Show help without examples

        """
        if method:
            self._show_method_help(method, show_examples=show_examples)
        else:
            self._show_overview_help(show_examples=show_examples)

    def _show_overview_help(self, *, show_examples=True):
        """Display overview of all available methods."""
        print("=" * 80)
        print("DataVis Class - Comprehensive Data Visualization Tool")
        print("=" * 80)
        print(f"Current Theme: {self.current_theme}")
        print(f"Available Themes: {', '.join(self.themes.keys())}")
        print("\n📊 AVAILABLE METHODS:\n")

        methods_info = [
            {
                "name": "plot_one",
                "description": "Plot a single time series from a DataFrame",
                "params": "df, column, date_column",
                "use_case": "Single metric tracking over time",
            },
            {
                "name": "plot_two",
                "description": "Compare two metrics from different DataFrames",
                "params": "data_config, same_axis=True",
                "use_case": "Comparative analysis of two time series",
            },
            {
                "name": "plot_chart",
                "description": "Create various chart types (line, bar, scatter, etc.)",
                "params": "data_config",
                "use_case": "Flexible charting with multiple chart types",
            },
            {
                "name": "plot_correlation",
                "description": "Generate correlation heatmaps",
                "params": 'df, columns=None, method="pearson"',
                "use_case": "Analyze relationships between variables",
            },
            {
                "name": "plot_sankey",
                "description": "Create Sankey diagrams for flow visualization",
                "params": "df, source_col, target_col, value_col, title=None, color_mapping=None",
                "use_case": "Visualize flow/process data",
            },
            {
                "name": "set_theme",
                "description": "Set global theme for all charts",
                "params": "theme_name",
                "use_case": "Consistent styling across visualizations",
            },
            {
                "name": "help",
                "description": "Get detailed help for methods",
                "params": "method=None, show_examples=True",
                "use_case": "Learn how to use the visualization tools",
            },
        ]

        for i, method in enumerate(methods_info, 1):
            print(f"{i}. {method['name']}")
            print(f"   📝 Description: {method['description']}")
            print(f"   ⚙️  Parameters: {method['params']}")
            print(f"   🎯 Use Case: {method['use_case']}")
            print()

        if show_examples:
            print("💡 QUICK START EXAMPLES:")
            print("   vis.help('plot_one')           # Get detailed help for plot_one")
            print("   vis.set_theme('dark')          # Switch to dark theme")
            print("   vis.plot_one(df, 'sales', 'date')  # Plot sales over time")
            print("   vis.plot_correlation(df)       # Create correlation heatmap")
            print()

        print("🔧 For detailed help on any method, use: vis.help('method_name')")
        print("=" * 80)

    def _show_method_help(self, method_name, *, show_examples=True):
        """Display detailed help for a specific method."""
        if not hasattr(self, method_name):
            print(f"❌ Method '{method_name}' not found!")
            print(
                f"Available methods: {[m for m in dir(self) if not m.startswith('_') and callable(getattr(self, m))]}"
            )
            return

        method = getattr(self, method_name)

        print("=" * 60)
        print(f"📊 DETAILED HELP: {method_name}")
        print("=" * 60)

        # Get docstring
        doc = inspect.getdoc(method)
        if doc:
            print(f"📝 {doc}")
            print()

        # Get method signature
        sig = inspect.signature(method)
        print(f"🔧 Signature: {method_name}{sig}")
        print()

        # Method-specific examples
        if show_examples:
            examples = self._get_method_examples(method_name)
            if examples:
                print("💡 EXAMPLES:")
                for example in examples:
                    print(f"   {example}")
                print()

        print("=" * 60)

    def _get_method_examples(self, method_name):
        """Get examples for specific methods."""
        examples = {
            "plot_one": [
                "vis.plot_one(df, 'sales', 'date')  # Plot sales over time",
                "vis.plot_one(stock_df, 'price', 'timestamp')  # Stock price chart",
            ],
            "plot_two": [
                "config = {'df1': df1, 'col1': 'sales', 'df2': df2, 'col2': 'revenue', 'date_column': 'date'}",
                "vis.plot_two(config, same_axis=True)  # Same y-axis",
                "vis.plot_two(config, same_axis=False)  # Separate y-axes",
            ],
            "plot_chart": [
                "config = {'df': df, 'date_col': 'date', 'value_cols': ['sales'], 'chart_type': 'line'}",
                "vis.plot_chart(config)  # Line chart",
                "config['chart_type'] = 'bar'  # Change to bar chart",
            ],
            "plot_correlation": [
                "vis.plot_correlation(df)  # All numeric columns",
                "vis.plot_correlation(df, columns=['sales', 'profit', 'cost'])  # Specific columns",
                "vis.plot_correlation(df, method='spearman')  # Spearman correlation",
            ],
            "plot_sankey": [
                "# Basic multi-layer Sankey",
                "vis.plot_sankey(df, 'Source', 'Target', 'Value')",
                "",
                "# Sankey with custom colors and title",
                "color_map = {",
                "    'Brand Media': 'rgba(246, 107, 109, 0.6)',",
                "    'TV': 'rgba(246, 107, 109, 0.6)',",
                "    'default': 'rgba(175, 175, 175, 0.6)'",
                "}",
                "vis.plot_sankey(df, 'Source', 'Target', 'Value', title='Brand Media Effects', color_mapping=color_map)",
            ],
            "set_theme": [
                "vis.set_theme('dark')  # Switch to dark theme",
                "vis.set_theme('business')  # Professional business theme",
                "vis.set_theme('scientific')  # Scientific publication theme",
            ],
        }
        return examples.get(method_name, [])

    def set_theme(self, theme_name):
        """
        Set the global theme for all charts.

        Parameters
        ----------
        theme_name : str
            Theme name. Available options: 'default', 'dark', 'business', 'scientific'

        Returns
        -------
        None

        Examples
        --------
        vis.set_theme('dark')      # Dark theme with plasma colors
        vis.set_theme('business')  # Professional business theme
        vis.set_theme('scientific') # Scientific publication theme

        """
        if theme_name not in self.themes:
            available_themes = ", ".join(self.themes.keys())
            error_msg = (
                f"Theme '{theme_name}' not found. Available themes: {available_themes}"
            )
            raise ValueError(error_msg)

        self.current_theme = theme_name
        print(f"✅ Theme set to: {theme_name}")

    def _apply_theme(self, fig):
        """Apply current theme to a figure."""
        theme = self.themes[self.current_theme]

        fig.update_layout(
            template=theme["template"],
            plot_bgcolor=theme["background_color"],
            font={
                "family": theme["font_family"],
                "size": theme["font_size"],
                "color": theme["text_color"],
            },
            xaxis={
                "showline": True,
                "linecolor": theme["text_color"],
                "gridcolor": theme["grid_color"],
            },
            yaxis={
                "showline": True,
                "linecolor": theme["text_color"],
                "gridcolor": theme["grid_color"],
                "rangemode": "tozero",
            },
        )

        return fig

    def plot_correlation(self, df, columns=None, method="pearson", title=None):
        """
        Create a correlation heatmap for numeric columns in a DataFrame.

        Parameters
        ----------
        df : pandas.DataFrame
            Input DataFrame with numeric columns
        columns : list, optional
            Specific columns to include in correlation. If None, uses all numeric columns
        method : str, default 'pearson'
            Correlation method: 'pearson', 'kendall', 'spearman'
        title : str, optional
            Custom title for the heatmap

        Returns
        -------
        plotly.graph_objects.Figure
            The correlation heatmap figure

        Example:
        --------
        # Basic correlation heatmap
        fig = vis.plot_correlation(df)

        # Specific columns with Spearman correlation
        fig = vis.plot_correlation(df, columns=['sales', 'profit', 'cost'], method='spearman')

        """
        # Select numeric columns
        if columns is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        else:
            numeric_cols = [
                col
                for col in columns
                if col in df.columns and df[col].dtype in ["int64", "float64"]
            ]

        # Minimum columns required for correlation
        min_correlation_cols = 2

        if len(numeric_cols) < min_correlation_cols:
            error_msg = "Need at least 2 numeric columns for correlation analysis"
            raise ValueError(error_msg)

        # Calculate correlation matrix
        corr_matrix = df[numeric_cols].corr(method=method)

        # Create heatmap
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale=self.themes[self.current_theme]["colorscale"],
            title=title or f"{method.title()} Correlation Matrix",
        )

        # Apply theme
        fig = self._apply_theme(fig)

        # Update text color for better readability
        fig.update_traces(
            textfont={"color": self.themes[self.current_theme]["text_color"]}
        )

        return fig

    def plot_sankey(self, df, source_col, target_col, value_col, **kwargs):
        """
        Create a multi-layer Sankey diagram from a single DataFrame.

        Parameters
        ----------
        df : pandas.DataFrame
            Input DataFrame with source, target, and value columns
        source_col : str
            Column name for source nodes
        target_col : str
            Column name for target nodes
        value_col : str
            Column name for flow values (must be numeric)
        title : str, optional
            Custom title for the diagram
        color_mapping : dict, optional
            Dictionary mapping source/target names to colors
            Format: {'Brand Media': 'rgba(246, 107, 109, 0.6)', 'default': 'rgba(175, 175, 175, 0.6)'}
            Pass as keyword argument: color_mapping={...}
        **kwargs : dict
            Additional keyword arguments including title and color_mapping

        Returns
        -------
        plotly.graph_objects.Figure
            The multi-layer Sankey diagram figure

        DataFrame Format Requirements:
        -----------------------------
        Single DataFrame with all flow data:
        | Source      | Target    | Value |
        |-------------|-----------|-------|
        | Brand Media | TV        | 100   |
        | Brand Media | Radio     | 50    |
        | TV          | BU_North  | 60    |
        | TV          | BU_South  | 40    |
        | Radio       | BU_North  | 30    |

        Example:
        --------
        # Basic multi-layer Sankey
        fig = vis.plot_sankey(df, 'Source', 'Target', 'Value')

        # Sankey with custom colors
        color_map = {
            'Brand Media': 'rgba(246, 107, 109, 0.6)',
            'TV': 'rgba(246, 107, 109, 0.6)',
            'Radio': 'rgba(246, 107, 109, 0.6)',
            'default': 'rgba(175, 175, 175, 0.6)'
        }
        fig = vis.plot_sankey(df, 'Source', 'Target', 'Value',
                             title='Brand Media Effects', color_mapping=color_map)

        """
        # Extract keyword arguments
        title = kwargs.get("title")
        color_mapping = kwargs.get("color_mapping")

        # Validate required columns
        required_cols = [source_col, target_col, value_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            error_msg = f"Missing columns: {missing_cols}"
            raise ValueError(error_msg)

        # Ensure value column is numeric
        if not pd.api.types.is_numeric_dtype(df[value_col]):
            error_msg = f"Value column '{value_col}' must be numeric"
            raise ValueError(error_msg)

        # Create working copy and remove any rows with missing values or zero values
        work_df = df[required_cols].dropna()
        work_df = work_df[work_df[value_col] != 0]  # Remove zero values

        if work_df.empty:
            error_msg = "No valid data rows found after removing missing/zero values"
            raise ValueError(error_msg)

        # Get all unique nodes
        all_sources = set(work_df[source_col].unique())
        all_targets = set(work_df[target_col].unique())

        # Create layers for proper node positioning
        # Layer 1: sources that don't appear as targets (starting nodes)
        layer_1_nodes = list(all_sources - all_targets)
        # Final layer: targets that don't appear as sources (ending nodes)
        final_layer_nodes = list(all_targets - all_sources)
        # Intermediate: nodes that are both source and target
        intermediate_nodes = list(all_sources & all_targets)

        # Create ordered node list for proper left-to-right flow
        all_nodes = layer_1_nodes + intermediate_nodes + final_layer_nodes
        node_dict = {node: i for i, node in enumerate(all_nodes)}

        # Create source, target, and value lists for Sankey
        source_indices = [node_dict[source] for source in work_df[source_col]]
        target_indices = [node_dict[target] for target in work_df[target_col]]
        values = work_df[value_col].tolist()

        # Apply color mapping if provided
        if color_mapping:
            link_colors = []
            for _, row in work_df.iterrows():
                source_name = row[source_col]
                target_name = row[target_col]
                if source_name in color_mapping:
                    link_colors.append(color_mapping[source_name])
                elif target_name in color_mapping:
                    link_colors.append(color_mapping[target_name])
                else:
                    link_colors.append(
                        color_mapping.get("default", "rgba(175, 175, 175, 0.6)")
                    )
        else:
            # Use theme-based default colors
            link_colors = (
                "rgba(255,255,255,0.3)"
                if self.current_theme == "dark"
                else "rgba(0,0,0,0.3)"
            )

        # Create Sankey diagram
        fig = go.Figure(
            data=[
                go.Sankey(
                    node={
                        "pad": 15,
                        "thickness": 20,
                        "line": {"color": "black", "width": 0.5},
                        "label": all_nodes,
                        "color": self.themes[self.current_theme]["line_color"],
                    },
                    link={
                        "source": source_indices,
                        "target": target_indices,
                        "value": values,
                        "color": link_colors,
                    },
                )
            ]
        )

        fig.update_layout(
            title_text=title or f"Sankey Diagram - {source_col} to {target_col}",
            font_size=self.themes[self.current_theme]["font_size"],
            font_color=self.themes[self.current_theme]["text_color"],
            paper_bgcolor=self.themes[self.current_theme]["background_color"],
        )

        return fig

    def plot_one(self, df1, col1, date_column):
        """
        Plots specified column from a DataFrame with themed styling.

        Uses a specified date column as the X-axis.

        Parameters
        ----------
        df1 : pandas.DataFrame
            Input DataFrame
        col1 : str
            Column name from the DataFrame to plot
        date_column : str
            The name of the date column to use for the X-axis

        Returns
        -------
        plotly.graph_objects.Figure
            The line plot figure

        """
        # Check if columns exist in the DataFrame
        if col1 not in df1.columns or date_column not in df1.columns:
            error_msg = "Column not found in DataFrame"
            raise ValueError(error_msg)

        # Check if the date column is in datetime format, if not convert it
        if not pd.api.types.is_datetime64_any_dtype(df1[date_column]):
            try:
                df1[date_column] = pd.to_datetime(df1[date_column], dayfirst=True)
            except (ValueError, TypeError) as e:
                error_msg = f"Error converting {date_column} to datetime: {e}"
                raise ValueError(error_msg) from e

        # Plotting using Plotly Express
        fig = px.line(df1, x=date_column, y=col1)

        # Apply theme
        fig = self._apply_theme(fig)

        return fig

    def plot_two(self, data_config, *, same_axis=True, title="Comparison Plot"):
        """
        Plots specified columns from two different DataFrames with themed styling.

        Parameters
        ----------
        data_config : dict
            Dictionary with keys: 'df1', 'col1', 'df2', 'col2', 'date_column'
        same_axis : bool, default True
            If True, plot both traces on the same y-axis; otherwise, use separate y-axes
        title : str, default "Comparison Plot"
            Custom title for the plot

        Returns
        -------
        plotly.graph_objects.Figure
            The comparison plot figure

        """
        # Extract parameters from config
        df1 = data_config["df1"]
        col1 = data_config["col1"]
        df2 = data_config["df2"]
        col2 = data_config["col2"]
        date_column = data_config["date_column"]

        # Validate inputs
        if col1 not in df1.columns or date_column not in df1.columns:
            error_msg = (
                f"Column {col1} or {date_column} not found in the first DataFrame."
            )
            raise ValueError(error_msg)
        if col2 not in df2.columns or date_column not in df2.columns:
            error_msg = (
                f"Column {col2} or {date_column} not found in the second DataFrame."
            )
            raise ValueError(error_msg)

        # Ensure date columns are in datetime format
        df1[date_column] = pd.to_datetime(df1[date_column], errors="coerce")
        df2[date_column] = pd.to_datetime(df2[date_column], errors="coerce")

        # Drop rows with invalid dates
        df1 = df1.dropna(subset=[date_column])
        df2 = df2.dropna(subset=[date_column])

        # Create traces
        trace1 = go.Scatter(
            x=df1[date_column],
            y=df1[col1],
            mode="lines",
            name=col1,
            yaxis="y1",
            line={"color": self.themes[self.current_theme]["line_color"]},
        )

        if same_axis:
            trace2 = go.Scatter(
                x=df2[date_column],
                y=df2[col2],
                mode="lines",
                name=col2,
                yaxis="y1",
            )
        else:
            trace2 = go.Scatter(
                x=df2[date_column],
                y=df2[col2],
                mode="lines",
                name=col2,
                yaxis="y2",
            )

        # Create figure
        fig = go.Figure(data=[trace1, trace2])

        # Apply theme
        fig = self._apply_theme(fig)

        # Update layout for dual axis if needed
        if not same_axis:
            fig.update_layout(
                yaxis2={
                    "title": f"{col2} (y2)",
                    "overlaying": "y",
                    "side": "right",
                    "showline": True,
                    "linecolor": self.themes[self.current_theme]["text_color"],
                    "rangemode": "tozero",
                }
            )

        # Update layout with custom title and legend positioning
        fig.update_layout(
            title=title,
            showlegend=True,
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "center",
                "x": 0.5
            }
        )

        return fig

    def plot_chart(self, data_config):
        """
        Plot various types of charts using Plotly with themed styling.

        Parameters
        ----------
        data_config : dict
            Configuration dictionary with keys:
            - df: DataFrame containing the data
            - date_col: The name of the column with date information
            - value_cols: List of columns to plot
            - chart_type: Type of chart ('line', 'bar', 'scatter', etc.)
            - title: Title of the chart
            - x_title: Title of the x-axis
            - y_title: Title of the y-axis
            - kwargs: Additional keyword arguments

        Returns
        -------
        plotly.graph_objects.Figure
            The chart figure

        """
        # Extract parameters with defaults
        dataframe = data_config["df"]
        date_col = data_config["date_col"]
        value_cols = data_config["value_cols"]
        chart_type = data_config.get("chart_type", "line")
        title = data_config.get("title", "Chart")
        x_title = data_config.get("x_title", "Date")
        y_title = data_config.get("y_title", "Values")
        kwargs = data_config.get("kwargs", {})

        # Ensure the date column is in datetime format
        dataframe[date_col] = pd.to_datetime(dataframe[date_col])

        # Validate input columns
        value_cols = [
            col for col in value_cols if col in dataframe.columns and col != date_col
        ]
        if not value_cols:
            error_msg = "No valid columns provided for plotting."
            raise ValueError(error_msg)

        # Initialize the figure
        fig = go.Figure()

        # Define a mapping for chart types to corresponding Plotly trace types
        chart_trace_map = {
            "line": lambda col: go.Scatter(
                x=dataframe[date_col],
                y=dataframe[col],
                mode="lines",
                name=col,
                **kwargs,
            ),
            "bar": lambda col: go.Bar(
                x=dataframe[date_col], y=dataframe[col], name=col, **kwargs
            ),
            "scatter": lambda col: go.Scatter(
                x=dataframe[date_col],
                y=dataframe[col],
                mode="markers",
                name=col,
                **kwargs,
            ),
            "area": lambda col: go.Scatter(
                x=dataframe[date_col],
                y=dataframe[col],
                mode="lines",
                fill="tozeroy",
                name=col,
                **kwargs,
            ),
        }

        # Generate traces for the selected chart type
        if chart_type in chart_trace_map:
            for col in value_cols:
                trace = chart_trace_map[chart_type](col)
                fig.add_trace(trace)
        else:
            error_msg = f"Unsupported chart type: {chart_type}"
            raise ValueError(error_msg)

        # Apply theme
        fig = self._apply_theme(fig)

        # Update the layout
        fig.update_layout(
            title=title,
            xaxis_title=x_title,
            yaxis_title=y_title,
            legend_title="Series",
        )

        return fig
