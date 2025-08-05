from visdata import CompareMeasurementsPlot, Measurement, MeasurementResult


def get_example_measurements():
    own_measurement = Measurement(
        "Own measurement",
        {
            r"$\alpha$": MeasurementResult(1, statistical=0.1, systematic=0.05),
            r"$\beta$": MeasurementResult(9.3, statistical=0.05, systematic=0.1),
            r"$\gamma$": MeasurementResult(3, statistical=0.2, systematic=0.3),
            r"$\delta$": MeasurementResult(2, statistical=0.3, systematic=0.35),
        },
    )

    publication_1 = Measurement(
        "Publication 1",
        {
            r"$\alpha$": MeasurementResult(1.3, statistical=0.1, systematic=0.4),
            r"$\gamma$": MeasurementResult(3.5, statistical=0.2, systematic=0.3),
        },
    )

    publication_2 = Measurement(
        "Publication 2",
        {
            r"$\alpha$": MeasurementResult(0.9, statistical=0.08, systematic=0.1),
            r"$\beta$": MeasurementResult(8, statistical=0.8, systematic=0.9),
            r"$\delta$": MeasurementResult(2.2, statistical=0.08, systematic=0.15),
        },
    )

    return own_measurement, publication_1, publication_2


def test_compare_measurement_plot_runs_without_error():
    measurements = get_example_measurements()
    compare_plot = CompareMeasurementsPlot(*measurements)
    fig, axs, handles, labels = compare_plot.plot(ncols=2)

    assert fig is not None
    assert axs.shape == (2, 2)
    assert len(handles) == 3
    assert labels[0] == "Own measurement"
    assert labels[1] == "Publication 1"
    assert labels[2] == "Publication 2"
