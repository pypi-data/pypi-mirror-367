import click
from pyHarm_cli.commands import project_admin
from pyHarm_cli.commands import project_add
import os
from pyHarm._kernel_state import load_kernel_state, save_kernel_state
import datetime

def _get_modifying_projet(ctx, project_name:str) : 
    active_project = ctx.obj.get('active_project')
    _project_name = None 
    if project_name : 
        _project_name = project_name 
        if (active_project) : 
            if ((project_name!=active_project)) :
                click.secho(f"Modifying project: {project_name} : ", fg="yellow", bold=True, nl=False)
        else : click.secho(f"({project_name}) : ", fg="green", bold=True, nl=False)
    else : 
        if active_project :  _project_name = active_project
        else :
            raise click.UsageError("No project name provided and no active project is set.")
    return _project_name

@click.group()
@click.version_option(package_name='pyHarm-os')
@click.pass_context
def pyharm_cli(ctx: click.Context) -> None:
    ctx_cli = load_kernel_state().get('cli', {})
    active_project = ctx_cli.get('active_project')
    if active_project : click.secho(f"({active_project}) : ", fg="green", bold=True, nl=False)
    # Make 'active_project' available to all subcommands via context
    ctx.ensure_object(dict)
    ctx.obj['active_project'] = active_project
    pass

@pyharm_cli.command(help="create a new pyHarm project")
@click.argument('project_name')
def new(project_name:str) -> None : 
    project_admin._new_project(project_name=project_name)
    pass

@pyharm_cli.command(help="puts project_name as actively modified")
@click.argument('project_name', required=False)
@click.pass_context
def activate(ctx, project_name:str) -> None :
    if project_name : project_admin._activate_project(project_name=project_name)
    else : 
        _project_name = _get_modifying_projet(ctx=ctx, project_name=project_name)
        if _project_name : click.echo(f"Current active project is '{_project_name}'.")
        else : click.echo(f"No project is currently active.")
    pass

@pyharm_cli.command(help="remove anyproject from being actively modifed")
def deactivate() -> None : 
    project_admin._deactivate_project()
    pass

@pyharm_cli.command(help="check if project seems viable to be run")
@click.option('--project', '-p', help="Project name (if not using active project)")
@click.pass_context
def check(ctx, project:str) -> None :
    _project_name = _get_modifying_projet(ctx=ctx, project_name=project)
    project_admin._check_if_project_viable(project_name=_project_name, verbose=True)
    pass

@pyharm_cli.command(help="remove an existing pyHarm project")
@click.argument('project_name')
@click.option("--force", "-f", is_flag=True, help="Force the removal")
def remove(project_name:str, force:bool = False) -> None : 
    project_admin._remove_project(project_name=project_name, force_removal=force)
    pass

@pyharm_cli.command(help="update a pyHarm project lock file")
@click.option('--project', '-p', help="Project name (if not using active project)")
@click.pass_context
def update(ctx, project:str) -> None : 
    _project_name = _get_modifying_projet(ctx=ctx, project_name=project)
    project_admin._update_project_lock(project_name=_project_name, force=True)
    pass

@pyharm_cli.command(help="add a file to track in a pyHarm project lock file")
@click.argument('file_path')
@click.option('--project', '-p', help="Project name (if not using active project)")
@click.pass_context
def track(ctx, project:str, file_path:str) -> None : 
    _project_name = _get_modifying_projet(ctx=ctx, project_name=project)
    project_admin._track_file(project_name=_project_name, file_path=file_path)
    pass

@pyharm_cli.command(help="remove a file to track in a pyHarm project lock file")
@click.argument('file_path')
@click.option('--project', '-p', help="Project name (if not using active project)")
@click.pass_context
def untrack(ctx, project:str, file_path:str) -> None : 
    _project_name = _get_modifying_projet(ctx=ctx, project_name=project)
    project_admin._untrack_file(project_name=_project_name, file_path=file_path)
    pass

@pyharm_cli.command(help="run a pyHarm project")
@click.option('--project', '-p', help="Project name (if not using active project)")
@click.option("--verbose", "-v", is_flag=True, help="Add verbosity viable check")
@click.option("--force", "-f", is_flag=True, help="Force lock file update -- can lead to data loss")
@click.pass_context
def run(ctx, project:str, verbose:bool=False, force:bool=False) -> None : 
    _project_name = _get_modifying_projet(ctx=ctx, project_name=project)
    project_admin._check_if_project_viable(project_name=_project_name, verbose=verbose)
    project_admin._update_project_lock(project_name=_project_name, force=force)
    project_admin._run_project(project_name=_project_name)
    pass

@pyharm_cli.command(help="Make a jupyter notebook from the python script")
@click.argument('export_type', type=click.Choice(list(project_admin.EXPORT_OPTIONS.keys())))
@click.option('--project', '-p', help="Project name (if not using active project)")
@click.pass_context
def export(ctx, project:str, export_type:str) -> None : 
    _project_name = _get_modifying_projet(ctx=ctx, project_name=project)
    project_admin._export_project(project_name=_project_name, export_type=export_type)
    pass

@pyharm_cli.command(help="Clear pyHarm project from all results")
@click.option('--project', '-p', help="Project name (if not using active project)")
@click.pass_context
def clear(ctx, project:str) -> None : 
    _project_name = _get_modifying_projet(ctx=ctx, project_name=project)
    project_admin._clear_results(project_name=_project_name)
    pass

@pyharm_cli.command(help="Complete the input files with default classes settings a pyHarm project")
@click.argument('cls', type=click.Choice(list(project_add.dict_filling.keys())))
@click.option('--project', '-p', help="Project name (if not using active project)")
@click.option("--type", "-t", help="Subclass of selected class")
@click.option("--name", "-n", help="Name to give instance of the class")
@click.option("--optional", "-o", is_flag=True, help="Add the optional arguments in the input files")
@click.option("--interactive", "-i", is_flag=True, help="Interactive filling of the class parameters")
@click.pass_context
def add(ctx, cls: str, project:str=None, type:str=None, name:str=None, optional:bool=None, interactive:bool=None) -> None :
# def add(ctx, cls: str, project:str=None,) -> None :
    _project_name = _get_modifying_projet(ctx=ctx, project_name=project)
    try :  
        object_type = project_add._select_cls_type(cls=cls, type=type)
        # object_cls = project_add.ADD_OPTIONS[cls][object_type]
        if not name : name=""
        project_add._complete_inputfiles(project_name=_project_name, cls=cls, object_type=object_type, name=name, optional=optional, interactive=interactive)
    except KeyboardInterrupt:
        click.echo("\nOperation aborted by user.")
        raise  # Re-raise the exception to exit the program
    pass


@pyharm_cli.command(help="Show user config file of pyHarm")
@click.option('--project', '-p', help="Project name (if not using active project)")
@click.option('--path', is_flag=True, help="get absolute path toward the user configuration file")
@click.pass_context
def config(ctx, project:str=None, path:bool=False):
    if path : 
        from pathlib import Path
        _path = Path.cwd() / ".pyHarm" / "settings.json"
        click.echo(f"User config file is stored in {_path}")
        return None 
    try :
        _project_name = _get_modifying_projet(ctx=ctx, project_name=project)
        _user_only = False
    except : 
        _project_name = None
        _user_only = True
    project_admin._config_show(project_name=_project_name, user_only=_user_only)
    pass


if __name__ == "__main__":
    pyharm_cli()
