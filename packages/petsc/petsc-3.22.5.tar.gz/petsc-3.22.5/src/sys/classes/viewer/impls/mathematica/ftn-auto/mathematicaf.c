#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mathematica.c */
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

#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewermathematicaopen_ PETSCVIEWERMATHEMATICAOPEN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewermathematicaopen_ petscviewermathematicaopen
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewermathematicaclearname_ PETSCVIEWERMATHEMATICACLEARNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewermathematicaclearname_ petscviewermathematicaclearname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewermathematicagetvector_ PETSCVIEWERMATHEMATICAGETVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewermathematicagetvector_ petscviewermathematicagetvector
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewermathematicaputvector_ PETSCVIEWERMATHEMATICAPUTVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewermathematicaputvector_ petscviewermathematicaputvector
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscviewermathematicaopen_(MPI_Fint * comm,int *port, char machine[], char mode[],PetscViewer *v, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1)
{
  char *_cltmp0 = PETSC_NULLPTR;
  char *_cltmp1 = PETSC_NULLPTR;
PetscBool v_null = !*(void**) v ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(v);
/* insert Fortran-to-C conversion for machine */
  FIXCHAR(machine,cl0,_cltmp0);
/* insert Fortran-to-C conversion for mode */
  FIXCHAR(mode,cl1,_cltmp1);
*ierr = PetscViewerMathematicaOpen(
	MPI_Comm_f2c(*(comm)),*port,_cltmp0,_cltmp1,v);
  FREECHAR(machine,_cltmp0);
  FREECHAR(mode,_cltmp1);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! v_null && !*(void**) v) * (void **) v = (void *)-2;
}
PETSC_EXTERN void  petscviewermathematicaclearname_(PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerMathematicaClearName(PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscviewermathematicagetvector_(PetscViewer viewer,Vec v, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLOBJECT(v);
*ierr = PetscViewerMathematicaGetVector(PetscPatchDefaultViewers((PetscViewer*)viewer),
	(Vec)PetscToPointer((v) ));
}
PETSC_EXTERN void  petscviewermathematicaputvector_(PetscViewer viewer,Vec v, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLOBJECT(v);
*ierr = PetscViewerMathematicaPutVector(PetscPatchDefaultViewers((PetscViewer*)viewer),
	(Vec)PetscToPointer((v) ));
}
#if defined(__cplusplus)
}
#endif
