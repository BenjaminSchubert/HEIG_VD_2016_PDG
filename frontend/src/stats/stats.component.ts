import { Component, ViewChild } from "@angular/core";
import { StatisticsService } from "./stats.service";
import { IStatistics, IChartData, DataContainer } from "./stubs";
import { ChartComponent } from "../utils/components/chart.component";


/**
 * Component to display statistics about the project
 */
@Component({
    styleUrls: ["./stats.scss"],
    templateUrl: "./stats.html",
})
export class StatsComponent {
    /**
     * Data we want to display in our graph
     */
    public data: IChartData;

    /**
     * Defines options to send to the chart
     */
    // tslint:disable-next-line:no-any
    public options: any;

    // reference to the chart component
    @ViewChild(ChartComponent) public chart: ChartComponent;

    // labels we care about for statistics
    private datasetLabels = {
        active_users_per_month : {
            backgroundColor: "#0073e5",
            borderColor: "#0073e5",
            fill: false,
            label: "Active users per month",
        },
        meetings_per_user: {
            backgroundColor: "#a94442",
            borderColor: "#a94442",
            fill: false,
            label: "Meetings per IUser",
        },
        new_users: {
            backgroundColor: "rgba(71, 188, 47, 0.91)",
            borderColor: "rgba(71, 188, 47, 0.91)",
            fill: false,
            label: "New Users",
        },
    };

    // defines the default precision to display in the graph
    private defaultPrecision: string = DataContainer.MONTH;

    // wrapper that contains the data we want to display
    private dataContainer: DataContainer;

    constructor(public service: StatisticsService) {
        this.dataContainer = new DataContainer(this.datasetLabels);
        this.data = this.dataContainer.getData(this.defaultPrecision);
        this.options = this.getOptions(this.defaultPrecision);

        service.$.subscribe((stats: IStatistics) => {
            if (stats === null) {
                return;
            }

            this.dataContainer.updateData({
                active_users_per_month: stats.active_users_per_month,
                meetings_per_user: stats.meetings_per_user,
                new_users: stats.new_users,
            });
            this.data = this.dataContainer.getData(this.defaultPrecision);
        });
    }

    /**
     * Show the statistics for the given precision
     *
     * @param precision for which to show statistics
     */
    public showStats(precision: string) {
        this.data = this.dataContainer.getData(precision);
        this.options = this.getOptions(precision);
    }

    /**
     * Reset the chart zoom to its original value
     */
    public resetZoom() {
        this.chart.resetZoom();
    }

    /**
     * Get the options for the given precision.
     *
     * @param precision for which to get the options
     */
    private getOptions(precision: string) {
        return {
            legend: {
                labels: {
                    fontColor: "#abaeaf",
                    fontSize: 18,
                },
            },
            maintainAspectRatio: false,
            responsive: true,
            scales: {
                xAxes: [{
                    grdLines: {
                        tickMarkLength: 15,
                    },
                    ticks: {
                        autoSkip: true,
                        fontColor: "#abaeaf",
                        fontSize: 16,
                    },
                    time: {
                        displayFormats: {
                            "day": "YYYY-MMM-DD",
                            "month": "YYYY-MMM",
                            "year": "YYYY",
                        },
                        unit: precision,
                        unitStepSize: 1,
                    },
                    type: "time",
                }],
                yAxes: [{
                    gridLines: {
                        tickMarkLength: 15,
                    },
                    ticks: {
                        autoSkip: true,
                        fontColor: "#abaeaf",
                        fontSize: 16,
                        min: 0,
                        stepSize: 1,
                    },
                }],
            },
            tooltips: {
                backgroundColor: "#232525",
                bodyFontColor: "#abaeaf",
                bodyFontSize: 15,
                bodySpacing: 4,
                titleFontColor: "#abaeaf",
                titleFontSize: 18,
                xPadding: 10,
                yPadding: 10,
            },
            zoom: {
                drag: true,
                enabled: true,
                limits: {
                    max: 10,
                    min: 0.5,
                },
                mode: "x",
            },
        };
    }

}
