/**
 * Global interface for the statistics we get from the server
 */
export interface IStatistics {
    new_users: IDailyStat[];
    meetings_per_user: IDailyStat[];
    active_users_per_month: IDailyStat[];
    total_meetings: number;
    total_users: number;
}

/**
 * Interface for statistics containers
 */
export interface IDailyStatContainer {
    [key: string]: IDailyStat[];
}

/**
 * Interface for data that is send to the chart.js backend for drawing
 */
export interface IChartData {
    labels: string[];
    datasets: IDataSet[];
}

/**
 * Interface of a dataset, used by Chart.js
 */
interface IDataSet {
    // tslint:disable-next-line:no-any
    [key: string]: any;
    data: number[];
}

/**
 * Interface for statistics about usage for a given day
 */
interface IDailyStat {
    number: number;
    day: string;
}


/**
 * This class is a utility class to order our statistics by day, month and year.
 *
 * This exposes utilities to update the current data and to fetch it for a given precision level (day, month, year).
 */
export class DataContainer {
    /**
     * Key to get daily statistics
     */
    public static readonly DAY = "day";

    /**
     * Key to get monthly statistics
     */
    public static readonly MONTH = "month";

    /**
     * Key to get yearly statistics
     */
    public static readonly YEAR = "year";

    /**
     * List of all possible keys
     */
    public static readonly PRECISIONS = [DataContainer.DAY, DataContainer.MONTH, DataContainer.YEAR];

    // tslint:disable-next-line:no-any
    private additionalDatasetInformation: {[key: string]: {[key: string]: any}};
    private labels: {[precision: string]: string[]};
    private datasets: {[key: string]: {[precision: string]: number[]}};

    /**
     * Create a new `DataContainer` with the given expected labels.
     *
     * Note that if you don't give labels, no statistics will be kept by the container, as they define
     * which values are of interest.
     *
     *
     * @param datasetLabels a javascript object mapping keys to look for in the statistics to their title.
     */
    // tslint:disable-next-line:no-any
    constructor(datasetLabels: {[key: string]: {[key: string]: any}}) {
        this.clearData(datasetLabels);
    }

    /**
     * Get the data for a given precision.
     *
     * Note that the precision must be a value from `PRECISIONS`. No checks are made to be sure the key
     * is indeed valid. You should refer to these values by their export variables, in order to ensure
     * they stay valid if the class internals change.
     *
     * @param precision at which to get the statistics
     * @returns {{datasets: IDataSet[], labels: string[]}}
     */
    public getData(precision: string): IChartData {
        let datasets: IDataSet[] = [];

        // tslint:disable-next-line:forin
        for (let key in this.additionalDatasetInformation) {
            let dataset: IDataSet = {
                data: this.datasets[key][precision],
            };

            // tslint:disable-next-line:forin
            for (let entry in this.additionalDatasetInformation[key]) {
                dataset[entry] = this.additionalDatasetInformation[key][entry];
            }

            datasets.push(dataset);
        }

        return {
            datasets: datasets,
            labels: this.labels[precision],
        };
    }

    /**
     * Update the internal data with the given statistics.
     *
     * Note that this will erase all previously available data.
     *
     * @param stats to be available through the container.
     */
    public updateData(stats: IDailyStatContainer) {
        if (stats === null) {
            return;
        }

        this.clearData();

        for (let key in stats) {
            if (stats[key].length === 0) {
                delete stats[key];
            }
        }

        let keys = Object.keys(stats);
        let indexes: {[key: string]: number} = {};

        for (let key of keys) {
            indexes[key] = 0;
        }

        while (true) {
            let min: {key: string, value: IDailyStat} = this.getOldestDateStats(stats, indexes);

            if (min === null) {
                break; // we treated everything
            }

            let date = new Date(min.value.day).toISOString().split("T")[0].split("-");

            let year = date[0];
            let month = `${year}-${date[1]}`;
            let day = `${month}-${date[2]}`;

            // conversion to a javascript Date object is required by the moment library we use afterwards
            // as a year is not a valid ISO date format.
            this.add_entry(min, DataContainer.YEAR, new Date(year).toISOString());
            this.add_entry(min, DataContainer.MONTH, month);
            this.add_entry(min, DataContainer.DAY, day);
        }
    }

    /**
     * Clean all internal data.
     *
     * @param datasetLabels optional labels to use as new keys to look for.
     */
    // tslint:disable-next-line:no-any
    private clearData(datasetLabels?: {[name: string]: {[key: string]: any}}) {
        if (datasetLabels === undefined) {
            datasetLabels = this.additionalDatasetInformation || {};
        }

        this.datasets = {};
        this.additionalDatasetInformation = {};
        this.labels = {};

        // tslint:disable-next-line:forin
        for (let name in datasetLabels) {
            this.additionalDatasetInformation[name] = datasetLabels[name];

            this.datasets[name] = {};
            for (let precision of DataContainer.PRECISIONS) {
                this.datasets[name][precision] = [];
            }
        }

        for (let precision of DataContainer.PRECISIONS) {
            // tslint:disable-next-line:no-any
            (<any> this.labels)[precision] = [];
        }

    }

    /**
     * Get the oldest day containing data for the given statistics.
     *
     * This will look for data at the given indexes, update the given indexes and return the new oldest data.
     *
     * If all data has been consumed, will return null.
     *
     * @param stats for which to get the oldest data
     * @param indexes at which to look for the oldest data
     * @returns {any} null or the new oldest data
     */
    private getOldestDateStats(stats: IDailyStatContainer, indexes: {[key: string]: number}) {
        let oldest: IDailyStat = null;
        let oldestKey: string = null;

        for (let key in stats) {
            if (oldest === null || stats[key][indexes[key]].day < oldest.day) {
                oldest = stats[key][indexes[key]];
                oldestKey = key;
            }
        }

        if (oldest === null) {
            // the stats object is empty, we consumed everything
            return null;
        }

        indexes[oldestKey]++;
        if (indexes[oldestKey] >= stats[oldestKey].length) {
            delete stats[oldestKey];
            delete indexes[oldestKey];
        }

        return {
            key: oldestKey,
            value: oldest,
        };
    }

    /**
     * Add a new entry to the internal data.
     *
     * This will make sure other entries have a "null" value, so we have consistent display in chart.js
     *
     * @param data to add
     * @param precision for which to add the data
     * @param xAxisValue
     */
    private add_entry(data: {key: string, value: IDailyStat}, precision: string, xAxisValue: string) {
        // tslint:disable:no-any
        if (
            (<any> this.labels)[precision].length === 0 ||
            xAxisValue > (<any> this.labels)[precision][(<any> this.labels)[precision].length - 1]
        ) {
            (<any> this.labels)[precision].push(xAxisValue);

            for (let dataset in this.datasets) {
                if (dataset === data.key) {
                    this.datasets[dataset][precision].push(data.value.number);
                } else {
                    this.datasets[dataset][precision].push(null);
                }
            }
        } else {
            this.datasets[data.key][precision][this.datasets[data.key][precision].length - 1] += data.value.number;
        }
        // tslint:enable:no-any
    }

}
