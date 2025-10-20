"""
Chart generation utilities for AI Smart Quiz App
Creates interactive charts and visualizations for analytics dashboard
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from utils.db_manager import db_manager
from utils.models import CategoryAnalytics, PerformanceTrend


class ChartGenerator:
    """Generates charts for the quiz application"""

    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3
        self.success_color = '#2ecc71'
        self.error_color = '#e74c3c'
        self.warning_color = '#f39c12'
        self.info_color = '#3498db'

    def create_category_performance_chart(self, analytics: List[CategoryAnalytics]) -> go.Figure:
        """Create bar chart showing average scores per category"""
        if not analytics:
            # Create empty chart
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig

        # Prepare data
        categories = [a.category_name for a in analytics]
        avg_scores = [a.average_score for a in analytics]
        attempts = [a.total_attempts for a in analytics]

        # Create subplots with secondary y-axis
        fig = make_subplots(
            specs=[[{"secondary_y": True}]],
            subplot_titles=("Average Score per Category",)
        )

        # Add bar chart for average scores
        colors = [self.success_color if score >= 70 else self.warning_color if score >= 50 else self.error_color
                 for score in avg_scores]

        fig.add_trace(
            go.Bar(
                x=categories,
                y=avg_scores,
                name="Average Score",
                marker_color=colors,
                text=[f"{score:.1f}%" for score in avg_scores],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Average Score: %{y:.1f}%<br>Attempts: %{customdata}<extra></extra>',
                customdata=attempts
            ),
            secondary_y=False
        )

        # Add line chart for attempts
        fig.add_trace(
            go.Scatter(
                x=categories,
                y=attempts,
                mode='lines+markers',
                name="Total Attempts",
                line=dict(color=self.info_color, width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>Attempts: %{y}<extra></extra>'
            ),
            secondary_y=True
        )

        # Update layout
        fig.update_xaxes(title_text="Categories", tickangle=45)
        fig.update_yaxes(title_text="Average Score (%)", secondary_y=False, range=[0, 100])
        fig.update_yaxes(title_text="Total Attempts", secondary_y=True)
        fig.update_layout(
            height=500,
            showlegend=True,
            hovermode='x unified'
        )

        return fig

    def create_attempts_distribution_chart(self, analytics: List[CategoryAnalytics]) -> go.Figure:
        """Create pie chart showing attempt distribution across categories"""
        if not analytics:
            # Create empty chart
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig

        # Filter categories with attempts
        categories_with_attempts = [a for a in analytics if a.total_attempts > 0]

        if not categories_with_attempts:
            fig = go.Figure()
            fig.add_annotation(
                text="No quiz attempts yet",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig

        # Prepare data
        labels = [a.category_name for a in categories_with_attempts]
        values = [a.total_attempts for a in categories_with_attempts]

        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker_colors=self.color_palette[:len(labels)],
            textinfo='label+percent+value',
            hovertemplate='<b>%{label}</b><br>Attempts: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])

        fig.update_layout(
            title="Quiz Attempts Distribution by Category",
            height=500,
            showlegend=True
        )

        return fig

    def create_performance_trend_chart(self, trend: Optional[PerformanceTrend]) -> go.Figure:
        """Create line chart showing performance trend over time"""
        if not trend or not trend.daily_scores:
            # Create empty chart
            fig = go.Figure()
            fig.add_annotation(
                text="No performance data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig

        # Prepare data
        dates = [pd.to_datetime(d['date']) for d in trend.daily_scores]
        avg_scores = [d['avg_score'] for d in trend.daily_scores]
        quiz_counts = [d['quiz_count'] for d in trend.daily_scores]

        # Create subplots
        fig = make_subplots(
            specs=[[{"secondary_y": True}]],
            subplot_titles=(f"Performance Trend - {trend.user_name} (Last {trend.period_days} Days)",)
        )

        # Add line chart for scores
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=avg_scores,
                mode='lines+markers',
                name="Average Score",
                line=dict(color=self.info_color, width=3),
                marker=dict(size=8),
                hovertemplate='Date: %{x}<br>Avg Score: %{y:.1f}%<extra></extra>'
            ),
            secondary_y=False
        )

        # Add bar chart for quiz count
        fig.add_trace(
            go.Bar(
                x=dates,
                y=quiz_counts,
                name="Quizzes Taken",
                marker_color=self.success_color,
                opacity=0.7,
                hovertemplate='Date: %{x}<br>Quizzes: %{y}<extra></extra>'
            ),
            secondary_y=True
        )

        # Add trend line
        if len(avg_scores) > 1:
            # Calculate simple linear trend
            import numpy as np
            x_numeric = np.arange(len(avg_scores))
            z = np.polyfit(x_numeric, avg_scores, 1)
            p = np.poly1d(z)
            trend_line = p(x_numeric)

            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=trend_line,
                    mode='lines',
                    name="Trend Line",
                    line=dict(color=self.warning_color, width=2, dash='dash'),
                    hovertemplate='Trend: %{y:.1f}%<extra></extra>'
                ),
                secondary_y=False
            )

        # Update layout
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Average Score (%)", secondary_y=False, range=[0, 100])
        fig.update_yaxes(title_text="Number of Quizzes", secondary_y=True)
        fig.update_layout(
            height=500,
            showlegend=True,
            hovermode='x unified'
        )

        return fig

    def create_score_distribution_chart(self, analytics: List[CategoryAnalytics]) -> go.Figure:
        """Create chart showing score distribution across grades"""
        if not analytics:
            # Create empty chart
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig

        # Aggregate score distribution across all categories
        grade_counts = {}
        total_scores = 0

        for category_analytics in analytics:
            for grade, count in category_analytics.score_distribution.items():
                grade_counts[grade] = grade_counts.get(grade, 0) + count
                total_scores += count

        if not grade_counts or total_scores == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="No score distribution data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig

        # Prepare data
        grades = list(grade_counts.keys())
        counts = list(grade_counts.values())
        percentages = [count / total_scores * 100 for count in counts]

        # Define colors for grades
        grade_colors = {
            'A (90-100)': self.success_color,
            'B (80-89)': self.info_color,
            'C (70-79)': self.warning_color,
            'D (60-69)': '#e67e22',
            'F (0-59)': self.error_color
        }

        colors = [grade_colors.get(grade, '#95a5a6') for grade in grades]

        # Create horizontal bar chart
        fig = go.Figure(data=[go.Bar(
            y=grades,
            x=percentages,
            orientation='h',
            marker_color=colors,
            text=[f"{count} ({pct:.1f}%)" for count, pct in zip(counts, percentages)],
            textposition='auto',
            hovertemplate='Grade: %{y}<br>Count: %{customdata}<br>Percentage: %{x:.1f}%<extra></extra>',
            customdata=counts
        )])

        fig.update_layout(
            title="Overall Score Distribution",
            xaxis_title="Percentage (%)",
            yaxis_title="Grade Ranges",
            height=400,
            xaxis=dict(range=[0, max(percentages) * 1.1] if percentages else [0, 100])
        )

        return fig

    def create_recent_activity_chart(self, days: int = 7) -> go.Figure:
        """Create chart showing recent quiz activity"""
        try:
            # Get recent results
            query = """
            SELECT DATE(completed_at) as date,
                   COUNT(*) as quiz_count,
                   AVG(score) as avg_score
            FROM results
            WHERE completed_at >= date('now', '-{} days')
            GROUP BY DATE(completed_at)
            ORDER BY date
            """.format(days)

            rows = db_manager.execute_query(query)

            if not rows:
                fig = go.Figure()
                fig.add_annotation(
                    text=f"No quiz activity in the last {days} days",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16)
                )
                return fig

            # Prepare data
            dates = [pd.to_datetime(row['date']) for row in rows]
            quiz_counts = [row['quiz_count'] for row in rows]
            avg_scores = [row['avg_score'] for row in rows]

            # Create subplots
            fig = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=(f"Recent Activity (Last {days} Days)",)
            )

            # Add bar chart for quiz count
            fig.add_trace(
                go.Bar(
                    x=dates,
                    y=quiz_counts,
                    name="Quizzes Completed",
                    marker_color=self.info_color,
                    hovertemplate='Date: %{x}<br>Quizzes: %{y}<extra></extra>'
                ),
                secondary_y=False
            )

            # Add line chart for average score
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=avg_scores,
                    mode='lines+markers',
                    name="Average Score",
                    line=dict(color=self.success_color, width=3),
                    marker=dict(size=8),
                    hovertemplate='Date: %{x}<br>Avg Score: %{y:.1f}%<extra></extra>'
                ),
                secondary_y=True
            )

            # Update layout
            fig.update_xaxes(title_text="Date")
            fig.update_yaxes(title_text="Quizzes Completed", secondary_y=False)
            fig.update_yaxes(title_text="Average Score (%)", secondary_y=True, range=[0, 100])
            fig.update_layout(
                height=400,
                showlegend=True,
                hovermode='x unified'
            )

            return fig

        except Exception as e:
            # Create error chart
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error loading activity data: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color='red')
            )
            return fig

    def create_user_leaderboard(self, limit: int = 10) -> go.Figure:
        """Create leaderboard showing top performers"""
        try:
            query = """
            SELECT user_name,
                   AVG(score) as avg_score,
                   COUNT(*) as quiz_count,
                   MAX(score) as best_score
            FROM results
            GROUP BY user_name
            HAVING quiz_count >= 3
            ORDER BY avg_score DESC
            LIMIT ?
            """

            rows = db_manager.execute_query(query, (limit,))

            if not rows:
                fig = go.Figure()
                fig.add_annotation(
                    text="No users with 3+ quizzes yet",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16)
                )
                return fig

            # Prepare data
            users = [row['user_name'] for row in rows]
            avg_scores = [row['avg_score'] for row in rows]
            quiz_counts = [row['quiz_count'] for row in rows]
            best_scores = [row['best_score'] for row in rows]

            # Create bar chart
            fig = go.Figure(data=[go.Bar(
                x=avg_scores,
                y=users,
                orientation='h',
                marker_color=self.success_color,
                text=[f"{score:.1f}%" for score in avg_scores],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Avg Score: %{x:.1f}%<br>Quizzes: %{customdata[0]}<br>Best Score: %{customdata[1]}%<extra></extra>',
                customdata=[[qc, bs] for qc, bs in zip(quiz_counts, best_scores)]
            )])

            fig.update_layout(
                title=f"Top {limit} Performers (Min 3 Quizzes)",
                xaxis_title="Average Score (%)",
                yaxis_title="User",
                height=max(400, len(users) * 40),
                xaxis=dict(range=[0, 100])
            )

            return fig

        except Exception as e:
            # Create error chart
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error loading leaderboard: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color='red')
            )
            return fig


# Global chart generator instance
chart_generator = ChartGenerator()


def create_analytics_charts():
    """Create all analytics charts for the dashboard"""
    charts = {}

    try:
        # Get analytics data
        category_analytics = db_manager.get_category_analytics()

        # Category performance chart
        charts['category_performance'] = chart_generator.create_category_performance_chart(category_analytics)

        # Attempts distribution chart
        charts['attempts_distribution'] = chart_generator.create_attempts_distribution_chart(category_analytics)

        # Score distribution chart
        charts['score_distribution'] = chart_generator.create_score_distribution_chart(category_analytics)

        # Recent activity chart
        charts['recent_activity'] = chart_generator.create_recent_activity_chart(days=7)

        # User leaderboard
        charts['leaderboard'] = chart_generator.create_user_leaderboard(limit=10)

    except Exception as e:
        st.error(f"Error creating analytics charts: {str(e)}")

    return charts


def display_analytics_dashboard():
    """Display the complete analytics dashboard"""
    st.markdown("## 📊 Performance Analytics Dashboard")

    # Create filters
    col1, col2, col3 = st.columns(3)

    with col1:
        days_filter = st.selectbox(
            "Time Period",
            options=[7, 14, 30, 90],
            index=0,
            format_func=lambda x: f"Last {x} days"
        )

    with col2:
        category_filter = st.selectbox(
            "Category Filter",
            options=["All Categories"] + [c.name for c in db_manager.get_categories()],
            index=0
        )

    with col3:
        if st.button("🔄 Refresh Data"):
            st.rerun()

    # Generate and display charts
    charts = create_analytics_charts()

    # Display charts in a grid
    if 'category_performance' in charts:
        st.plotly_chart(charts['category_performance'], use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        if 'attempts_distribution' in charts:
            st.plotly_chart(charts['attempts_distribution'], use_container_width=True)

    with col2:
        if 'score_distribution' in charts:
            st.plotly_chart(charts['score_distribution'], use_container_width=True)

    if 'recent_activity' in charts:
        st.plotly_chart(charts['recent_activity'], use_container_width=True)

    if 'leaderboard' in charts:
        st.plotly_chart(charts['leaderboard'], use_container_width=True)

    # Additional statistics
    st.markdown("### 📈 Detailed Statistics")

    try:
        # Get overall statistics
        overall_stats_query = """
        SELECT
            COUNT(*) as total_quizzes,
            AVG(score) as avg_score,
            MAX(score) as best_score,
            MIN(score) as worst_score,
            COUNT(DISTINCT user_name) as unique_users
        FROM results
        """

        stats_rows = db_manager.execute_query(overall_stats_query)

        if stats_rows:
            stats = stats_rows[0]

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric("Total Quizzes", stats['total_quizzes'])

            with col2:
                st.metric("Average Score", f"{stats['avg_score']:.1f}%")

            with col3:
                st.metric("Best Score", f"{stats['best_score']}%")

            with col4:
                st.metric("Worst Score", f"{stats['worst_score']}%")

            with col5:
                st.metric("Unique Users", stats['unique_users'])

    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")


def display_user_performance_trend(user_name: str):
    """Display performance trend for a specific user"""
    try:
        trend = db_manager.get_performance_trend(user_name, days=30)

        if trend:
            st.markdown(f"### 📈 Performance Trend for {user_name}")

            # Trend chart
            chart = chart_generator.create_performance_trend_chart(trend)
            st.plotly_chart(chart, use_container_width=True)

            # Trend statistics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Average Score", f"{trend.average_score:.1f}%")

            with col2:
                st.metric("Total Quizzes", trend.total_quizzes)

            with col3:
                st.metric("Trend", trend.trend_direction.capitalize())

            with col4:
                st.metric("Period", f"{trend.period_days} days")

            # Recent scores
            if trend.daily_scores:
                st.markdown("#### Recent Performance")
                recent_scores = trend.daily_scores[-5:]  # Last 5 days
                for day_data in recent_scores:
                    date_str = pd.to_datetime(day_data['date']).strftime('%b %d')
                    st.write(f"**{date_str}**: {day_data['avg_score']:.1f}% ({day_data['quiz_count']} quizzes)")

        else:
            st.info(f"No performance data available for {user_name}")

    except Exception as e:
        st.error(f"Error loading performance trend: {str(e)}")