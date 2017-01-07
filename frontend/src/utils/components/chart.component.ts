// As no typings for charts 2.0 are available yet upstream we have to disable no-any
// tslint:disable:no-any

import { Component, Input, ElementRef, OnChanges, SimpleChanges, OnInit } from "@angular/core";

declare let Chart: any;


/**
 * This component is a wrapper around `Chart.js` charts.
 *
 * It supports automatically changing the chart and redrawing if needs be, using Angular2 mechanisms
 * of Input events.
 */
@Component({
    selector: "rd-chart",
    styles: [":host { display: flex; flex-grow: 1; }"],
    template: "<canvas></canvas>",
})
export class ChartComponent implements OnInit, OnChanges {
    /**
     * Define the type of the chart to display.
     */
    @Input() public type: string;

    /**
     * Define the data to be displayed.
     */
    @Input() public data: any;

    /**
     * Define options to pass to the chart object.
     */
    @Input() public options: any;

    private chart: any;

    constructor(private elementRef: ElementRef) {
    }

    public ngOnInit() {
        this.createChart();
    }

    /**
     * Check whether we can automatically update the chart and do it.
     * Otherwise, destroy the current chart and redraw one.
     *
     * @param changes that occurred since last check
     */
    public ngOnChanges(changes: SimpleChanges) {
        if (this.chart && changes["data"]) {
            let currentValue = changes["data"].currentValue;
            ["datasets", "labels", "xLabels", "yLabels"].forEach((property: any) => {
                this.chart.data[property] = currentValue[property];
            });
            this.chart.config.data.labels = currentValue["labels"];
            this.chart.update();
        }

        if (this.chart && (changes["type"] || changes["options"])) {
            this.chart.destroy();
            this.createChart();
        }
    }

    /**
     * Reset the zoom of the chart.
     *
     * This needs the chartjs-plugin-zoom to be installed
     */
    public resetZoom() {
        this.chart.resetZoom();
    }

    /**
     * Create a new chart with the current options, data and type.
     */
    private createChart() {
        this.chart = new Chart(this.elementRef.nativeElement.querySelector("canvas"), {
            data: this.data,
            options: this.options,
            type: this.type,
        });
    }
}
