#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* cgnsv.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscviewer.h"
#include "petscdmplex.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewercgnsopen_ PETSCVIEWERCGNSOPEN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewercgnsopen_ petscviewercgnsopen
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewercgnssetsolutionindex_ PETSCVIEWERCGNSSETSOLUTIONINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewercgnssetsolutionindex_ petscviewercgnssetsolutionindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewercgnsgetsolutionindex_ PETSCVIEWERCGNSGETSOLUTIONINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewercgnsgetsolutionindex_ petscviewercgnsgetsolutionindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewercgnsgetsolutiontime_ PETSCVIEWERCGNSGETSOLUTIONTIME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewercgnsgetsolutiontime_ petscviewercgnsgetsolutiontime
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewercgnsgetsolutionname_ PETSCVIEWERCGNSGETSOLUTIONNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewercgnsgetsolutionname_ petscviewercgnsgetsolutionname
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscviewercgnsopen_(MPI_Fint * comm, char name[],PetscFileMode *type,PetscViewer *viewer, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
PetscBool viewer_null = !*(void**) viewer ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(viewer);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscViewerCGNSOpen(
	MPI_Comm_f2c(*(comm)),_cltmp0,*type,viewer);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! viewer_null && !*(void**) viewer) * (void **) viewer = (void *)-2;
}
PETSC_EXTERN void  petscviewercgnssetsolutionindex_(PetscViewer viewer,PetscInt *solution_id, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerCGNSSetSolutionIndex(PetscPatchDefaultViewers((PetscViewer*)viewer),*solution_id);
}
PETSC_EXTERN void  petscviewercgnsgetsolutionindex_(PetscViewer viewer,PetscInt *solution_id, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLINTEGER(solution_id);
*ierr = PetscViewerCGNSGetSolutionIndex(PetscPatchDefaultViewers((PetscViewer*)viewer),solution_id);
}
PETSC_EXTERN void  petscviewercgnsgetsolutiontime_(PetscViewer viewer,PetscReal *time,PetscBool *set, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLREAL(time);
*ierr = PetscViewerCGNSGetSolutionTime(PetscPatchDefaultViewers((PetscViewer*)viewer),time,set);
}
PETSC_EXTERN void  petscviewercgnsgetsolutionname_(PetscViewer viewer, char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerCGNSGetSolutionName(PetscPatchDefaultViewers((PetscViewer*)viewer),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
#if defined(__cplusplus)
}
#endif
