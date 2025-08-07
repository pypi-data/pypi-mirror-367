#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* matnull.c */
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

#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matnullspacecreaterigidbody_ MATNULLSPACECREATERIGIDBODY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matnullspacecreaterigidbody_ matnullspacecreaterigidbody
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matnullspaceview_ MATNULLSPACEVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matnullspaceview_ matnullspaceview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matnullspacecreate_ MATNULLSPACECREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matnullspacecreate_ matnullspacecreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matnullspacedestroy_ MATNULLSPACEDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matnullspacedestroy_ matnullspacedestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matnullspaceremove_ MATNULLSPACEREMOVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matnullspaceremove_ matnullspaceremove
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matnullspacetest_ MATNULLSPACETEST
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matnullspacetest_ matnullspacetest
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matnullspacecreaterigidbody_(Vec coords,MatNullSpace *sp, int *ierr)
{
CHKFORTRANNULLOBJECT(coords);
PetscBool sp_null = !*(void**) sp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sp);
*ierr = MatNullSpaceCreateRigidBody(
	(Vec)PetscToPointer((coords) ),sp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sp_null && !*(void**) sp) * (void **) sp = (void *)-2;
}
PETSC_EXTERN void  matnullspaceview_(MatNullSpace sp,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLOBJECT(viewer);
*ierr = MatNullSpaceView(
	(MatNullSpace)PetscToPointer((sp) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  matnullspacecreate_(MPI_Fint * comm,PetscBool *has_cnst,PetscInt *n, Vec vecs[],MatNullSpace *SP, int *ierr)
{
PetscBool vecs_null = !*(void**) vecs ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vecs);
PetscBool SP_null = !*(void**) SP ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(SP);
*ierr = MatNullSpaceCreate(
	MPI_Comm_f2c(*(comm)),*has_cnst,*n,vecs,SP);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vecs_null && !*(void**) vecs) * (void **) vecs = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! SP_null && !*(void**) SP) * (void **) SP = (void *)-2;
}
PETSC_EXTERN void  matnullspacedestroy_(MatNullSpace *sp, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(sp);
 PetscBool sp_null = !*(void**) sp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sp);
*ierr = MatNullSpaceDestroy(sp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sp_null && !*(void**) sp) * (void **) sp = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(sp);
 }
PETSC_EXTERN void  matnullspaceremove_(MatNullSpace sp,Vec vec, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLOBJECT(vec);
*ierr = MatNullSpaceRemove(
	(MatNullSpace)PetscToPointer((sp) ),
	(Vec)PetscToPointer((vec) ));
}
PETSC_EXTERN void  matnullspacetest_(MatNullSpace sp,Mat mat,PetscBool *isNull, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLOBJECT(mat);
*ierr = MatNullSpaceTest(
	(MatNullSpace)PetscToPointer((sp) ),
	(Mat)PetscToPointer((mat) ),isNull);
}
#if defined(__cplusplus)
}
#endif
