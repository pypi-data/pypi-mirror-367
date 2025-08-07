import os
import typer
from typing_extensions import Annotated
import geci_janitor as jn

janitor = typer.Typer(help="Tools to clean k9 data for the eradication Guadalupe Island project")


@janitor.command()
def transform_xlsx(options: str):
    """
    Transform data `IG_ESFUERZO_K9_{date}.xls[x]` \n
    """
    command = f"docker run --entrypoint clean_k9_data --volume $PWD:/workdir islasgeci/clean_k9_data {options}"
    os.system(command)


@janitor.command()
def clean_cameras(file: str):
    """
    Clean data `IG_CAMARA_TRAMPA_EXTRA_{date}.xls[x]` \n
    and `IG_CAMARA_TRAMPA_CAMINO_{date}.xls[x]` \n
    """
    salida_campo = "camaras_extra_revision_campo.csv"
    salida_memoria = "camaras_extra_revision_memoria.csv"
    command = f"docker run --entrypoint clean_k9_data --volume $PWD:/workdir islasgeci/clean_k9_data extra {file} --salida-campo={salida_campo} --salida-memoria={salida_memoria}"
    os.system(command)
    command = f'docker run --volume $PWD:/workdir islasgeci/clean_camera_data R -e \'cameraData::add_data_check_column_to_campo("{file}", "{salida_campo}", "with_date_{salida_campo}")\''
    os.system(command)
    command = f'docker run --volume $PWD:/workdir islasgeci/clean_camera_data R -e \'cameraData::add_data_check_column_to_memoria("{file}", "{salida_memoria}", "with_date_{salida_memoria}")\''
    os.system(command)


@janitor.command()
def check_cameras_ids(
    mapsource_path: str = typer.Option(),
    revision_campo_path: str = "with_date_camaras_extra_revision_campo.csv",
):
    """
    Check if all cameras are listed in Mapsource and revision_campo.
    """
    command = f'docker run --volume $PWD:/workdir islasgeci/read_mapsource Rscript -e \'readMS::check_cameras("{revision_campo_path}", "{mapsource_path}")\''
    os.system(command)


@janitor.command()
def cameras_info(file: str = "camaras_extra_revision_campo.csv"):
    """
    Get cameras info. Run after `clean-cameras` command.
    """
    command = f'docker run --volume $PWD:/workdir islasgeci/clean_camera_data R -e \'cameraData::write_camera_info("{file}", "cameras_info.csv")\''
    os.system(command)
    command = f'docker run --volume $PWD:/workdir islasgeci/clean_camera_data R -e \'cameraData::write_cameras_last_check("{file}", "cameras_last_check.csv")\''
    os.system(command)


@janitor.command(help="Clean and check IG_POSICION_TRAMPAS and IG_MORFOMETRIA")
def transform_cat_data(
    positions_path: Annotated[str, typer.Argument()],
    morphometry_path: Annotated[str, typer.Argument()],
):
    command = f"docker run --rm --volume $PWD:/data islasgeci/diferencias_morfometria_posicion_trampas:latest ./src/demo_workflow /data/{positions_path} /data/{morphometry_path}"
    os.system(command)


@janitor.command(help="Clean and check IS_POSICION_TRAMPAS and IS_MORFOMETRIA")
def transform_cat_data_socorro(
    positions_path: Annotated[str, typer.Argument()],
    morphometry_path: Annotated[str, typer.Argument()],
):
    command = f"docker run --rm --volume $PWD:/data islasgeci/diferencias_morfometria_posicion_trampas:latest ./src/demo_workflow /data/{positions_path} /data/{morphometry_path}"
    os.system(command)

    command = f"docker run --rm --volume $PWD:/data islasgeci/diferencias_morfometria_posicion_trampas:latest ./src/socorro_morphometry_happy_path.sh /data/{morphometry_path}"
    os.system(command)


@janitor.command(help="Extract weekly position traps data for Socorro monthly excel")
def extract_weeks_from_xlsx(excel_path):
    command = f"docker run --rm --volume $PWD:/data islasgeci/diferencias_morfometria_posicion_trampas:latest bash -c 'source src/extract_socorro_position_sheets.sh && extract_socorro_position /data/{excel_path}'"
    os.system(command)


@janitor.command()
def weekly_effort_summary(file: str):
    """
    Calculate summary from IG_POSICION_TRAMPAS_{date}_clean.csv \n
    """
    command = f"docker run --rm --volume $PWD:/workdir/datos islasgeci/datatools:latest ./src/get_weekly_summary.sh datos/{file}"
    os.system(command)


@janitor.command(help="Generate tidy and weekly effort tables for socorro monthly cat data")
def clean_socorro_week_data(week: int, data_file: str):
    command = f"docker run -v $PWD/results:/workdir/results -v $PWD:/workdir/data islasgeci/datatools bash -c 'python src/get_weekly_summary_socorro_from_excell.py {week} data/{data_file} && cambia_formato_fecha results/week_{week}.csv > results/week_{week}_iso.csv'"
    os.system(command)
    command = f"docker run -v $PWD/results:/workdir/results -v $PWD:/workdir/data islasgeci/diferencias_morfometria_posicion_trampas src/make_table_tidy.R --data results/socorro_cleaned_format.csv --salida results/tidy_{week}.csv"
    os.system(command)


@janitor.command()
def clean_socorro_position(socorro_position_path: Annotated[str, typer.Argument()]):
    """
    Clean weekly position traps from Socorro. \n
    Before run rename file with last sunday date: 'IS_POSICION_TRAMPA_09JUN2024.csv'. \n
    Run after `extract_weeks_from_xlsx` command. Next command is `weekly_effort_summary`
    """
    command = f"docker run --rm --volume $PWD:/datos islasgeci/diferencias_morfometria_posicion_trampas:latest ./src/happy_position_traps_socorro.sh /datos/{socorro_position_path}"

    os.system(command)


@janitor.command()
def validate(directory: Annotated[str, typer.Argument()] = "."):
    """
    Run tabular data package validation \n
    """
    command = (
        f"docker run --rm --volume $PWD:/workdir islasgeci/misctools geci-validate {directory}"
    )
    os.system(command)


@janitor.command()
def change_date_format_to_iso(file_path: Annotated[str, typer.Argument()]):
    """
    'cambia_formato_fecha' wrapper \n
    """
    command = f"docker run --rm --volume $PWD:/workdir islasgeci/base bash -c 'cambia_formato_fecha {file_path} > ISO_{file_path}'"
    os.system(command)


@janitor.command()
def version():
    version = jn.__version__
    print(version)


@janitor.command()
def update_images():
    """
    Update images for command: \n
    - `transform_cat_data`
    """
    os.system("pip install --upgrade geci-janitor")
    update_diferencias()
    update_clean_k9()
    update_clean_cameras()


def update_diferencias():
    command = "docker rmi --force islasgeci/diferencias_morfometria_posicion_trampas && docker pull islasgeci/diferencias_morfometria_posicion_trampas"
    os.system(command)


def update_clean_k9():
    command = "docker rmi --force islasgeci/clean_k9_data && docker pull islasgeci/clean_k9_data"
    os.system(command)


def update_clean_cameras():
    command = (
        "docker rmi --force islasgeci/clean_camera_data && docker pull islasgeci/clean_camera_data"
    )
    os.system(command)
