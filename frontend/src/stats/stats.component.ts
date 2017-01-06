import { Component } from "@angular/core";
import { StatisticsService } from "./stats.service";
import { IStatistics, IChartData, DataContainer } from "./stubs";


/**
 * Component to display statistics about the project
 */
@Component({
    template: `<rd-chart type="line" [data]="data" [options]="options"></rd-chart>`,
})
export class StatsComponent {
    /**
     * Data we want to display in our graph
     */
    public data: IChartData;

    /**
     * Defines options to send to the chart
     */
    public options = {
        maintainAspectRatio: false,
        responsive: true,
        scales: {
            xAxes: [{
                time: {
                    displayFormats: {
                        "day": "YYYY-MMM-DD",
                        "month": "YYYY-MMM",
                        "year": "YYYY",
                    },
                    unit: "month",
                    unitStepSize: 1,
                },
                type: "time",
            }],
            yAxes: [{
                ticks: {
                    min: 0,
                    stepSize: 1,
                },
            }],
        },
    };

    // labels we care about for statistics
    private datasetLabels = {
        meetings_per_user: "Meetings per User",
        new_users: "New Users",
    };

    // defines the precision to display in the graph
    private precision: string = DataContainer.MONTH;

    // wrapper that contains the data we want to display
    private dataContainer: DataContainer;

    constructor(service: StatisticsService) {
        this.dataContainer = new DataContainer(this.datasetLabels);
        this.data = this.dataContainer.getData(this.precision);

        service.$.subscribe((stats: IStatistics) => {
            if (stats === null) {
                return;
            }
            this.dataContainer.updateData({new_users: stats.new_users, meetings_per_user: stats.meetings_per_user});
            this.data = this.dataContainer.getData(this.precision);
        });
    }

}
